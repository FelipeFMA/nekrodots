#pragma GCC diagnostic ignored "-Wdeprecated-declarations"
#include "better_control.h"
#include <gtk/gtk.h>
#include <string.h>
#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>

// Forward declarations
static void refresh_wifi_list(GtkWidget *button, gpointer user_data);
static void toggle_wifi(GtkSwitch *switch_widget, gboolean state, gpointer user_data);
static void on_wifi_row_activated(GtkListBox *box, GtkListBoxRow *row, gpointer user_data);
static void on_wifi_connect_clicked(GtkWidget *button, gpointer user_data);
static void on_wifi_connect_response(GtkDialog *dialog, int response, gpointer user_data);
static void disconnect_wifi(GtkWidget *button, gpointer user_data);
static char* get_wifi_interface(void);
static void update_connection_status(GtkWidget *status_label);
static bool is_wifi_enabled(void);
static void show_connection_error(GtkWidget *parent, const char *error_message);
static GtkWidget* create_wifi_row(const char *ssid, int signal_strength, bool is_connected);

// Structure to hold WiFi page state
typedef struct {
    GtkWidget *status_label;
    GtkWidget *network_list;
    GtkWidget *refresh_button;
    GtkWidget *toggle_switch;
    GtkWidget *disconnect_button;
    char current_network[256];
    bool is_refreshing;
    GThread *refresh_thread;
} WiFiPageState;

// Global state
static WiFiPageState wifi_state = {0};
static char wifi_interface[32] = {0};

// Function to detect WiFi interface
static char* get_wifi_interface(void) {
    if (wifi_interface[0] != '\0') {
        return wifi_interface;
    }
    
    char *output = execute_command("nmcli device status | grep wifi | awk '{print $1}' | head -n 1");
    if (output && strlen(output) > 0) {
        // Remove trailing newline if present
        if (output[strlen(output) - 1] == '\n') {
            output[strlen(output) - 1] = '\0';
        }
        strncpy(wifi_interface, output, sizeof(wifi_interface) - 1);
        free(output);
        return wifi_interface;
    }
    
    // Fallback to wlan0 if no interface found
    strncpy(wifi_interface, "wlan0", sizeof(wifi_interface) - 1);
    return wifi_interface;
}

// Check if WiFi is enabled
static bool is_wifi_enabled(void) {
    char *output = execute_command("nmcli radio wifi");
    if (!output) {
        return false;
    }
    
    bool enabled = (strstr(output, "enabled") != NULL);
    free(output);
    return enabled;
}

// Get current connection info
static char* get_current_connection(void) {
    char *interface = get_wifi_interface();
    
    // First check if the interface is up and connected
    char status_cmd[128];
    snprintf(status_cmd, sizeof(status_cmd), 
             "nmcli -t device status | grep %s | grep -q connected", 
             interface);
    
    int status = system(status_cmd);
    if (status != 0) {
        // Interface is not connected
        return NULL;
    }
    
    // Try multiple commands to get the connection name
    char *output = NULL;
    
    // Method 1: Get from GENERAL.CONNECTION
    char command1[128];
    snprintf(command1, sizeof(command1), 
             "nmcli -t -f GENERAL.CONNECTION device show %s | cut -d: -f2", 
             interface);
    
    output = execute_command(command1);
    if (output && strlen(output) > 0 && strcmp(output, "--") != 0) {
        // Remove trailing newline if present
        if (output[strlen(output) - 1] == '\n') {
            output[strlen(output) - 1] = '\0';
        }
        
        // If not empty and not just dashes, return it
        if (strlen(output) > 0) {
            return output;
        }
        
        free(output);
    } else if (output) {
        free(output);
    }
    
    // Method 2: Try getting from connection show
    char command2[128];
    snprintf(command2, sizeof(command2), 
             "nmcli -t connection show --active | grep %s | cut -d: -f1", 
             interface);
    
    output = execute_command(command2);
    if (output && strlen(output) > 0) {
        // Remove trailing newline if present
        if (output[strlen(output) - 1] == '\n') {
            output[strlen(output) - 1] = '\0';
        }
        
        return output;
    } else if (output) {
        free(output);
    }
    
    // Method 3: Get from iwconfig
    char command3[128];
    snprintf(command3, sizeof(command3), 
             "iwconfig %s | grep 'ESSID:' | sed 's/.*ESSID:\"\\(.*\\)\".*/\\1/'", 
             interface);
    
    output = execute_command(command3);
    if (output && strlen(output) > 0 && strcmp(output, "off/any") != 0) {
        // Remove trailing newline if present
        if (output[strlen(output) - 1] == '\n') {
            output[strlen(output) - 1] = '\0';
        }
        
        return output;
    } else if (output) {
        free(output);
    }
    
    return NULL;
}

// Update connection status in the UI
static void update_connection_status(GtkWidget *status_label) {
    char *connection = get_current_connection();
    
    if (connection && strlen(connection) > 0) {
        char *status_text = g_strdup_printf("Connected to: %s", connection);
        gtk_label_set_text(GTK_LABEL(status_label), status_text);
        
        // Update global state
        strncpy(wifi_state.current_network, connection, sizeof(wifi_state.current_network) - 1);
        wifi_state.current_network[sizeof(wifi_state.current_network) - 1] = '\0';
        
        // Show disconnect button
        if (wifi_state.disconnect_button) {
            gtk_widget_set_visible(wifi_state.disconnect_button, TRUE);
        }
        
        g_free(status_text);
    } else {
        // Check if WiFi is enabled before showing "Not connected"
        if (is_wifi_enabled()) {
            gtk_label_set_text(GTK_LABEL(status_label), "Not connected to any network");
        } else {
            gtk_label_set_text(GTK_LABEL(status_label), "WiFi is turned off");
        }
        
        wifi_state.current_network[0] = '\0';
        
        // Hide disconnect button
        if (wifi_state.disconnect_button) {
            gtk_widget_set_visible(wifi_state.disconnect_button, FALSE);
        }
    }
    
    if (connection) free(connection);
}

// Create a row for the WiFi list
static GtkWidget* create_wifi_row(const char *ssid, int signal_strength, bool is_connected) {
    GtkWidget *row = gtk_list_box_row_new();
    GtkWidget *box = gtk_box_new(GTK_ORIENTATION_HORIZONTAL, 10);
    gtk_widget_set_margin_top(box, 5);
    gtk_widget_set_margin_bottom(box, 5);
    gtk_widget_set_margin_start(box, 5);
    gtk_widget_set_margin_end(box, 5);
    
    // Add SSID label
    GtkWidget *ssid_label = gtk_label_new(ssid);
    gtk_widget_set_hexpand(ssid_label, TRUE);
    gtk_label_set_xalign(GTK_LABEL(ssid_label), 0.0); // Left-align
    gtk_box_append(GTK_BOX(box), ssid_label);
    
    // Add connection indicator if connected
    if (is_connected) {
        GtkWidget *connected_label = gtk_label_new("✓");
        gtk_widget_add_css_class(connected_label, "success");
        gtk_box_append(GTK_BOX(box), connected_label);
    }
    
    // Add signal strength indicator
    char strength_text[16];
    snprintf(strength_text, sizeof(strength_text), "%d%%", signal_strength);
    
    GtkWidget *strength_label = gtk_label_new(strength_text);
    gtk_label_set_xalign(GTK_LABEL(strength_label), 1.0); // Right-align
    
    // Add CSS class based on signal strength
    if (signal_strength > 70) {
        gtk_widget_add_css_class(strength_label, "good-signal");
    } else if (signal_strength > 30) {
        gtk_widget_add_css_class(strength_label, "medium-signal");
    } else {
        gtk_widget_add_css_class(strength_label, "weak-signal");
    }
    
    gtk_box_append(GTK_BOX(box), strength_label);
    
    // Set the box as the row's child
    gtk_list_box_row_set_child(GTK_LIST_BOX_ROW(row), box);
    
    return row;
}

// Thread function for refreshing WiFi list
static gpointer refresh_wifi_list_thread(gpointer user_data) {
    GtkWidget *listbox = wifi_state.network_list;
    if (!listbox || !GTK_IS_LIST_BOX(listbox)) {
        return NULL;
    }
    
    // Clear existing items
    GtkWidget *child;
    while ((child = gtk_widget_get_first_child(listbox)) != NULL) {
        gtk_list_box_remove(GTK_LIST_BOX(listbox), child);
    }
    
    // Check if WiFi is enabled
    if (!is_wifi_enabled()) {
        GtkWidget *row = gtk_list_box_row_new();
        GtkWidget *label = gtk_label_new("WiFi is disabled");
        gtk_list_box_row_set_child(GTK_LIST_BOX_ROW(row), label);
        gtk_list_box_append(GTK_LIST_BOX(listbox), row);
        
        g_idle_add((GSourceFunc)gtk_widget_set_sensitive, wifi_state.refresh_button);
        wifi_state.is_refreshing = false;
        return NULL;
    }
    
    // Get current connection
    char *current_connection = get_current_connection();
    
    // Store current connection in global state for later use
    if (current_connection && strlen(current_connection) > 0) {
        strncpy(wifi_state.current_network, current_connection, sizeof(wifi_state.current_network) - 1);
        wifi_state.current_network[sizeof(wifi_state.current_network) - 1] = '\0';
    } else {
        wifi_state.current_network[0] = '\0';
    }
    
    // Get WiFi list with more details - fix the command
    char *output = execute_command("nmcli -t -f SSID,SIGNAL,SECURITY device wifi list");
    if (!output) {
        GtkWidget *row = gtk_list_box_row_new();
        GtkWidget *label = gtk_label_new("No networks found");
        gtk_list_box_row_set_child(GTK_LIST_BOX_ROW(row), label);
        gtk_list_box_append(GTK_LIST_BOX(listbox), row);
        
        if (current_connection) free(current_connection);
        g_idle_add((GSourceFunc)gtk_widget_set_sensitive, wifi_state.refresh_button);
        wifi_state.is_refreshing = false;
        return NULL;
    }
    
    // Parse and add networks
    char *saveptr;
    char *line = strtok_r(output, "\n", &saveptr);
    int networks_added = 0;
    GHashTable *seen_ssids = g_hash_table_new(g_str_hash, g_str_equal);
    
    while (line) {
        // Find the first colon (SSID:SIGNAL:SECURITY)
        char *signal_str = strchr(line, ':');
        if (signal_str) {
            *signal_str = '\0';
            signal_str++;
            
            // Skip empty SSIDs
            if (strlen(line) == 0) {
                line = strtok_r(NULL, "\n", &saveptr);
                continue;
            }
            
            // Skip if we've already seen this SSID
            if (g_hash_table_contains(seen_ssids, line)) {
                line = strtok_r(NULL, "\n", &saveptr);
                continue;
            }
            
            // Get signal strength
            char *security_str = strchr(signal_str, ':');
            int signal = 0;
            
            if (security_str) {
                *security_str = '\0';
                security_str++;
                signal = atoi(signal_str);
            } else {
                signal = atoi(signal_str);
            }
            
            // Check if this network is the current connection
            bool is_connected = false;
            if (current_connection && strcmp(line, current_connection) == 0) {
                is_connected = true;
            } else if (strlen(wifi_state.current_network) > 0 && strcmp(line, wifi_state.current_network) == 0) {
                is_connected = true;
            }
            
            // Create and add the row
            GtkWidget *row = create_wifi_row(line, signal, is_connected);
            gtk_list_box_append(GTK_LIST_BOX(listbox), row);
            networks_added++;
            
            // Mark this SSID as seen
            g_hash_table_add(seen_ssids, g_strdup(line));
        }
        line = strtok_r(NULL, "\n", &saveptr);
    }
    
    // Add a message if no networks were added
    if (networks_added == 0) {
        GtkWidget *row = gtk_list_box_row_new();
        GtkWidget *label = gtk_label_new("No networks found");
        gtk_list_box_row_set_child(GTK_LIST_BOX_ROW(row), label);
        gtk_list_box_append(GTK_LIST_BOX(listbox), row);
    }
    
    // Clean up
    g_hash_table_destroy(seen_ssids);
    free(output);
    if (current_connection) free(current_connection);
    
    // Re-enable refresh button
    g_idle_add((GSourceFunc)gtk_widget_set_sensitive, wifi_state.refresh_button);
    wifi_state.is_refreshing = false;
    
    return NULL;
}

// Refresh the WiFi network list
static void refresh_wifi_list(GtkWidget *button, gpointer user_data) {
    if (wifi_state.is_refreshing || wifi_state.refresh_thread) {
        return;
    }
    wifi_state.is_refreshing = true;
    
    // Disable refresh button during refresh
    if (wifi_state.refresh_button) {
        gtk_widget_set_sensitive(wifi_state.refresh_button, FALSE);
    }
    
    // Create and start a new thread for the refresh operation
    wifi_state.refresh_thread = g_thread_new("wifi_refresh", refresh_wifi_list_thread, NULL);
}

// Toggle WiFi on/off
static void toggle_wifi(GtkSwitch *switch_widget, gboolean state, gpointer user_data) {
    // Update UI to show we're working
    gtk_widget_set_sensitive(GTK_WIDGET(switch_widget), FALSE);
    
    if (wifi_state.status_label) {
        gtk_label_set_text(GTK_LABEL(wifi_state.status_label), 
                          state ? "Turning WiFi on..." : "Turning WiFi off...");
    }
    
    // Execute the command to toggle WiFi
    char command[32];
    snprintf(command, sizeof(command), "nmcli radio wifi %s", state ? "on" : "off");
    char *output = execute_command(command);
    if (output) {
        free(output);
    }
    
    // Short delay to allow system to update
    g_usleep(500000); // 500ms
    
    // Update UI based on new state
    if (state) {
        // Update connection status
        if (wifi_state.status_label) {
            update_connection_status(wifi_state.status_label);
        }
        
        // Refresh the network list
        refresh_wifi_list(NULL, NULL);
    } else {
        // Update status label
        if (wifi_state.status_label) {
            gtk_label_set_text(GTK_LABEL(wifi_state.status_label), "WiFi is turned off");
        }
        
        // Clear the network list
        if (wifi_state.network_list) {
            GtkWidget *child = gtk_widget_get_first_child(wifi_state.network_list);
            while (child) {
                GtkWidget *next = gtk_widget_get_next_sibling(child);
                gtk_list_box_remove(GTK_LIST_BOX(wifi_state.network_list), child);
                child = next;
            }
            
            // Add a message
            GtkWidget *row = gtk_list_box_row_new();
            GtkWidget *label = gtk_label_new("WiFi is disabled");
            gtk_list_box_row_set_child(GTK_LIST_BOX_ROW(row), label);
            gtk_list_box_append(GTK_LIST_BOX(wifi_state.network_list), row);
        }
        
        // Hide disconnect button
        if (wifi_state.disconnect_button) {
            gtk_widget_set_visible(wifi_state.disconnect_button, FALSE);
        }
    }
    
    // Re-enable the switch
    gtk_widget_set_sensitive(GTK_WIDGET(switch_widget), TRUE);
}

// Show connection error dialog
static void show_connection_error(GtkWidget *parent, const char *error_message) {
    GtkWidget *dialog = gtk_dialog_new_with_buttons(
        "Connection Error",
        GTK_WINDOW(parent),
        GTK_DIALOG_MODAL | GTK_DIALOG_DESTROY_WITH_PARENT,
        "OK", GTK_RESPONSE_OK,
        NULL
    );
    
    GtkWidget *content_area = gtk_dialog_get_content_area(GTK_DIALOG(dialog));
    gtk_widget_set_margin_top(content_area, 20);
    gtk_widget_set_margin_bottom(content_area, 20);
    gtk_widget_set_margin_start(content_area, 20);
    gtk_widget_set_margin_end(content_area, 20);
    
    GtkWidget *message_label = gtk_label_new("Failed to connect to network");
    gtk_box_append(GTK_BOX(content_area), message_label);
    
    GtkWidget *details_label = gtk_label_new(error_message);
    gtk_label_set_wrap(GTK_LABEL(details_label), TRUE);
    gtk_widget_set_margin_top(details_label, 10);
    gtk_box_append(GTK_BOX(content_area), details_label);
    
    g_signal_connect_swapped(dialog, "response", G_CALLBACK(gtk_window_destroy), dialog);
    gtk_window_present(GTK_WINDOW(dialog));
}

// Custom row activation handler
static void on_wifi_row_activated(GtkListBox *box, GtkListBoxRow *row, gpointer user_data) {
    if (!row || !GTK_IS_LIST_BOX_ROW(row)) {
        return;
    }
    
    // Get the parent window
    GtkWidget *parent_window = GTK_WIDGET(gtk_widget_get_root(GTK_WIDGET(box)));
    if (!parent_window) {
        return;
    }
    
    // Get the selected network SSID
    // The row structure is: row -> box -> ssid_label (first child)
    GtkWidget *row_box = gtk_list_box_row_get_child(row);
    if (!row_box) {
        return;
    }
    
    // Get the first child of the box, which is the SSID label
    GtkWidget *ssid_label = gtk_widget_get_first_child(row_box);
    if (!ssid_label || !GTK_IS_LABEL(ssid_label)) {
        return;
    }
    
    const char *ssid = gtk_label_get_text(GTK_LABEL(ssid_label));
    if (!ssid || strlen(ssid) == 0) {
        return;
    }
    
    // Check if this is a special row (like "WiFi is disabled")
    if (strcmp(ssid, "WiFi is disabled") == 0 || 
        strcmp(ssid, "No networks found") == 0) {
        return;
    }
    
    // Create a modern popup dialog
    GtkWidget *dialog = gtk_dialog_new_with_buttons(
        "WiFi Connection",
        GTK_WINDOW(parent_window),
        GTK_DIALOG_MODAL | GTK_DIALOG_DESTROY_WITH_PARENT,
        "Cancel", GTK_RESPONSE_CANCEL,
        "Connect", GTK_RESPONSE_ACCEPT,
        NULL
    );
    
    // Make the dialog look nicer
    gtk_window_set_default_size(GTK_WINDOW(dialog), 350, 150);
    
    // Create content area with message
    GtkWidget *content_area = gtk_dialog_get_content_area(GTK_DIALOG(dialog));
    gtk_widget_set_margin_top(content_area, 20);
    gtk_widget_set_margin_bottom(content_area, 20);
    gtk_widget_set_margin_start(content_area, 20);
    gtk_widget_set_margin_end(content_area, 20);
    
    GtkWidget *message_label = gtk_label_new(NULL);
    char *message = g_markup_printf_escaped(
        "<span size='large'>Connect to <b>%s</b>?</span>\n\n"
        "Do you want to connect to this WiFi network?",
        ssid
    );
    gtk_label_set_markup(GTK_LABEL(message_label), message);
    g_free(message);
    
    gtk_label_set_wrap(GTK_LABEL(message_label), TRUE);
    gtk_label_set_xalign(GTK_LABEL(message_label), 0.0);
    gtk_box_append(GTK_BOX(content_area), message_label);
    
    // Set the default response
    gtk_dialog_set_default_response(GTK_DIALOG(dialog), GTK_RESPONSE_ACCEPT);
    
    // Store the SSID as object data
    g_object_set_data_full(G_OBJECT(dialog), "ssid", g_strdup(ssid), g_free);
    
    // Connect response signal
    g_signal_connect(dialog, "response", G_CALLBACK(on_wifi_connect_response), NULL);
    
    // Show the dialog
    gtk_window_present(GTK_WINDOW(dialog));
}

// Handle the response from the WiFi connection dialog
static void on_wifi_connect_response(GtkDialog *dialog, int response, gpointer user_data) {
    // Get the SSID from the dialog's object data
    const char *ssid = g_object_get_data(G_OBJECT(dialog), "ssid");
    
    if (!ssid || strlen(ssid) == 0) {
        gtk_window_destroy(GTK_WINDOW(dialog));
        return;
    }
    
    if (response == GTK_RESPONSE_ACCEPT) {
        // First check if this network is already saved
        char check_cmd[256];
        snprintf(check_cmd, sizeof(check_cmd), 
                 "nmcli -t connection show | grep '%s' | wc -l", 
                 ssid);
        
        char *check_result = execute_command(check_cmd);
        bool is_saved = false;
        
        if (check_result) {
            is_saved = (atoi(check_result) > 0);
            free(check_result);
        }
        
        // Check if the network has security
        char security_cmd[256];
        snprintf(security_cmd, sizeof(security_cmd), 
                 "nmcli -t -f SSID,SECURITY device wifi list | grep '^%s:' | cut -d: -f2", 
                 ssid);
        
        char *security_result = execute_command(security_cmd);
        bool has_security = false;
        
        if (security_result) {
            has_security = (strlen(security_result) > 0 && 
                           strcmp(security_result, "--") != 0 && 
                           strcmp(security_result, "\n") != 0);
            free(security_result);
        } else {
            // If we can't determine security, assume it has security
            has_security = true;
        }
        
        // If the network is saved or doesn't have security, connect directly
        if (is_saved || !has_security) {
            // Proceed with connection
            char command[256];
            snprintf(command, sizeof(command), "nmcli device wifi connect '%s'", ssid);
            
            char *output = execute_command(command);
            
            if (output && strstr(output, "successfully")) {
                // Store the connected network name
                strncpy(wifi_state.current_network, ssid, sizeof(wifi_state.current_network) - 1);
                wifi_state.current_network[sizeof(wifi_state.current_network) - 1] = '\0';
                
                update_connection_status(wifi_state.status_label);
                refresh_wifi_list(NULL, NULL);
            } else {
                show_connection_error(dialog, 
                                     output ? output : "Failed to connect to network");
            }
            
            if (output) free(output);
        } else {
            // Network requires password, show password dialog
            GtkWidget *parent_window = GTK_WIDGET(gtk_widget_get_root(GTK_WIDGET(dialog)));
            
            // Create password dialog
            GtkWidget *pwd_dialog = gtk_dialog_new_with_buttons(
                "WiFi Password",
                GTK_WINDOW(parent_window),
                GTK_DIALOG_MODAL | GTK_DIALOG_DESTROY_WITH_PARENT,
                "Cancel", GTK_RESPONSE_CANCEL,
                "Connect", GTK_RESPONSE_ACCEPT,
                NULL
            );
            
            // Make the dialog look nicer
            gtk_window_set_default_size(GTK_WINDOW(pwd_dialog), 350, 200);
            
            // Create content area
            GtkWidget *content_area = gtk_dialog_get_content_area(GTK_DIALOG(pwd_dialog));
            gtk_widget_set_margin_top(content_area, 20);
            gtk_widget_set_margin_bottom(content_area, 20);
            gtk_widget_set_margin_start(content_area, 20);
            gtk_widget_set_margin_end(content_area, 20);
            
            // Add network name
            GtkWidget *network_label = gtk_label_new(NULL);
            char *network_text = g_markup_printf_escaped(
                "<span size='large'>Enter password for <b>%s</b></span>",
                ssid
            );
            gtk_label_set_markup(GTK_LABEL(network_label), network_text);
            g_free(network_text);
            
            gtk_label_set_wrap(GTK_LABEL(network_label), TRUE);
            gtk_label_set_xalign(GTK_LABEL(network_label), 0.0);
            gtk_box_append(GTK_BOX(content_area), network_label);
            
            // Add password entry
            GtkWidget *password_entry = gtk_password_entry_new();
            gtk_password_entry_set_show_peek_icon(GTK_PASSWORD_ENTRY(password_entry), TRUE);
            gtk_widget_set_margin_top(password_entry, 10);
            gtk_widget_set_margin_bottom(password_entry, 10);
            gtk_box_append(GTK_BOX(content_area), password_entry);
            
            // Set the default response
            gtk_dialog_set_default_response(GTK_DIALOG(pwd_dialog), GTK_RESPONSE_ACCEPT);
            
            // Store data for the connect button
            GtkWidget *connect_button = gtk_dialog_get_widget_for_response(
                GTK_DIALOG(pwd_dialog), GTK_RESPONSE_ACCEPT);
                
            g_object_set_data_full(G_OBJECT(connect_button), "ssid", g_strdup(ssid), g_free);
            g_object_set_data(G_OBJECT(connect_button), "password_entry", password_entry);
            g_object_set_data(G_OBJECT(connect_button), "dialog", pwd_dialog);
            
            // Connect the button click handler
            g_signal_connect(connect_button, "clicked", G_CALLBACK(on_wifi_connect_clicked), NULL);
            
            // Show the dialog
            gtk_window_present(GTK_WINDOW(pwd_dialog));
        }
    }
    
    // Destroy the original dialog
    gtk_window_destroy(GTK_WINDOW(dialog));
}

// Handler for WiFi connect button click
static void on_wifi_connect_clicked(GtkWidget *button, gpointer user_data) {
    GtkWidget *dialog = GTK_WIDGET(g_object_get_data(G_OBJECT(button), "dialog"));
    GtkWidget *entry = GTK_WIDGET(g_object_get_data(G_OBJECT(button), "password_entry"));
    const char *ssid = g_object_get_data(G_OBJECT(button), "ssid");
    
    if (!ssid || strlen(ssid) == 0) {
        show_connection_error(dialog, "Invalid network name");
        return;
    }
    
    const char *password = gtk_editable_get_text(GTK_EDITABLE(entry));
    
    // Disable the button to prevent multiple clicks
    gtk_widget_set_sensitive(button, FALSE);
    
    // Update status label if visible
    if (wifi_state.status_label) {
        char *status_text = g_strdup_printf("Connecting to %s...", ssid);
        gtk_label_set_text(GTK_LABEL(wifi_state.status_label), status_text);
        g_free(status_text);
    }
    
    // Connect to the network
    char command[1024];
    snprintf(command, sizeof(command), 
             "nmcli device wifi connect \"%s\" password \"%s\"", 
             ssid, password);
    
    char *output = execute_command(command);
    if (output) {
        if (strstr(output, "successfully activated") != NULL) {
            // Connection successful
            free(output);
            
            // Store the connected network name
            strncpy(wifi_state.current_network, ssid, sizeof(wifi_state.current_network) - 1);
            wifi_state.current_network[sizeof(wifi_state.current_network) - 1] = '\0';
            
            // Close the dialog
            gtk_window_destroy(GTK_WINDOW(dialog));
            
            // Update status and refresh list
            if (wifi_state.status_label) {
                update_connection_status(wifi_state.status_label);
            }
            refresh_wifi_list(NULL, NULL);
        } else {
            // Show error message
            show_connection_error(dialog, output);
            free(output);
            
            // Re-enable the button
            gtk_widget_set_sensitive(button, TRUE);
        }
    } else {
        // Show generic error
        show_connection_error(dialog, "Unknown error occurred while connecting");
        
        // Re-enable the button
        gtk_widget_set_sensitive(button, TRUE);
    }
}

// Disconnect from current WiFi network
static void disconnect_wifi(GtkWidget *button, gpointer user_data) {
    (void) user_data;
    // Check if we're connected
    if (strlen(wifi_state.current_network) == 0) {
        return;
    }
    
    // Update status label
    if (wifi_state.status_label) {
        gtk_label_set_text(GTK_LABEL(wifi_state.status_label), "Disconnecting...");
    }
    
    // Disable the button to prevent multiple clicks
    gtk_widget_set_sensitive(button, FALSE);
    
    // Get WiFi interface
    char *interface = get_wifi_interface();
    
    // Disconnect command
    char command[128];
    snprintf(command, sizeof(command), "nmcli device disconnect %s", interface);
    
    char *output = execute_command(command);
    if (output) {
        free(output);
    }
    
    // Update status and refresh list
    if (wifi_state.status_label) {
        update_connection_status(wifi_state.status_label);
    }
    refresh_wifi_list(NULL, NULL);
    
    // Re-enable the button
    gtk_widget_set_sensitive(button, TRUE);
}

// Initialize the WiFi page
void init_wifi_page(GtkWidget *notebook, AppState *state) {
    (void) state;
    // Main container
    GtkWidget *wifi_box = gtk_box_new(GTK_ORIENTATION_VERTICAL, 10);
    gtk_widget_set_margin_top(wifi_box, 10);
    gtk_widget_set_margin_bottom(wifi_box, 10);
    gtk_widget_set_margin_start(wifi_box, 10);
    gtk_widget_set_margin_end(wifi_box, 10);

    // Create header with toggle switch
    GtkWidget *header_box = gtk_box_new(GTK_ORIENTATION_HORIZONTAL, 10);
    
    GtkWidget *wifi_label = gtk_label_new("WiFi");
    gtk_widget_set_hexpand(wifi_label, TRUE);
    gtk_label_set_xalign(GTK_LABEL(wifi_label), 0.0); // Left-align
    gtk_box_append(GTK_BOX(header_box), wifi_label);
    
    // Create WiFi toggle switch
    GtkWidget *wifi_toggle = gtk_switch_new();
    
    // Set initial state based on actual WiFi state
    bool wifi_enabled = is_wifi_enabled();
    gtk_switch_set_active(GTK_SWITCH(wifi_toggle), wifi_enabled);
    
    gtk_box_append(GTK_BOX(header_box), wifi_toggle);
    gtk_box_append(GTK_BOX(wifi_box), header_box);
    
    // Create status label
    GtkWidget *status_label = gtk_label_new("");
    gtk_label_set_xalign(GTK_LABEL(status_label), 0.0); // Left-align
    gtk_widget_set_margin_bottom(status_label, 10);
    gtk_box_append(GTK_BOX(wifi_box), status_label);
    
    // Create action buttons box
    GtkWidget *action_box = gtk_box_new(GTK_ORIENTATION_HORIZONTAL, 10);
    
    // Create disconnect button
    GtkWidget *disconnect_button = gtk_button_new_with_label("Disconnect");
    g_signal_connect(disconnect_button, "clicked", G_CALLBACK(disconnect_wifi), NULL);
    gtk_box_append(GTK_BOX(action_box), disconnect_button);
    
    // Create refresh button
    GtkWidget *refresh_button = gtk_button_new_with_label("Refresh Networks");
    gtk_widget_set_hexpand(refresh_button, TRUE);
    gtk_box_append(GTK_BOX(action_box), refresh_button);
    
    gtk_box_append(GTK_BOX(wifi_box), action_box);
    
    // Create networks list with title
    GtkWidget *networks_label = gtk_label_new("Available Networks");
    gtk_label_set_xalign(GTK_LABEL(networks_label), 0.0); // Left-align
    gtk_widget_set_margin_top(networks_label, 10);
    gtk_box_append(GTK_BOX(wifi_box), networks_label);

    // WiFi list
    GtkWidget *wifi_list = gtk_list_box_new();
    gtk_list_box_set_selection_mode(GTK_LIST_BOX(wifi_list), GTK_SELECTION_SINGLE);
    gtk_widget_set_vexpand(wifi_list, TRUE);
    gtk_box_append(GTK_BOX(wifi_box), wifi_list);

    // Create scrolled window
    GtkWidget *scrolled = gtk_scrolled_window_new();
    gtk_scrolled_window_set_policy(GTK_SCROLLED_WINDOW(scrolled),
                                 GTK_POLICY_AUTOMATIC,
                                 GTK_POLICY_AUTOMATIC);
    gtk_scrolled_window_set_child(GTK_SCROLLED_WINDOW(scrolled), wifi_box);
    
    // Add to notebook
    GtkWidget *label = gtk_label_new("WiFi");
    gtk_notebook_append_page(GTK_NOTEBOOK(notebook), scrolled, label);

    // Store widgets in global state
    wifi_state.status_label = status_label;
    wifi_state.network_list = wifi_list;
    wifi_state.refresh_button = refresh_button;
    wifi_state.toggle_switch = wifi_toggle;
    wifi_state.disconnect_button = disconnect_button;
    wifi_state.is_refreshing = false;
    
    // Set initial visibility of disconnect button
    char *current_connection = get_current_connection();
    if (current_connection && strlen(current_connection) > 0) {
        strncpy(wifi_state.current_network, current_connection, sizeof(wifi_state.current_network) - 1);
        free(current_connection);
    } else {
        wifi_state.current_network[0] = '\0';
        gtk_widget_set_visible(disconnect_button, FALSE);
    }
    
    // Connect signals
    g_signal_connect(wifi_toggle, "state-set", G_CALLBACK(toggle_wifi), NULL);
    
    // Create a custom row activation handler
    g_signal_connect(wifi_list, "row-activated", G_CALLBACK(on_wifi_row_activated), NULL);
    
    g_signal_connect(refresh_button, "clicked", G_CALLBACK(refresh_wifi_list), NULL);
    
    // Set initial status
    update_connection_status(status_label);
    
    // Initial refresh of network list
    refresh_wifi_list(NULL, NULL);
}
    
    // Initial refresh of network list
    refresh_wifi_list(NULL, NULL);
}