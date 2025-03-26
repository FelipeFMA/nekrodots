#include "better_control.h"
#include <gtk/gtk.h>
#include <string.h>
#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>

// Forward declarations
static void refresh_wifi_list(GtkWidget *button, gpointer user_data);
static void toggle_wifi(GtkSwitch *switch_widget, gboolean state, gpointer user_data);
static void connect_wifi(GtkListBoxRow *row, gpointer user_data);
static void on_wifi_connect_clicked(GtkWidget *button, gpointer user_data);
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
    
    char command[128];
    snprintf(command, sizeof(command), 
             "nmcli -t -f GENERAL.CONNECTION device show %s | cut -d: -f2", 
             interface);
    
    char *output = execute_command(command);
    if (!output || strlen(output) == 0) {
        if (output) free(output);
        return NULL;
    }
    
    // Remove trailing newline if present
    if (output[strlen(output) - 1] == '\n') {
        output[strlen(output) - 1] = '\0';
    }
    
    return output;
}

// Update connection status in the UI
static void update_connection_status(GtkWidget *status_label) {
    char *connection = get_current_connection();
    
    if (connection && strlen(connection) > 0) {
        char *status_text = g_strdup_printf("Connected to: %s", connection);
        gtk_label_set_text(GTK_LABEL(status_label), status_text);
        
        // Update global state
        strncpy(wifi_state.current_network, connection, sizeof(wifi_state.current_network) - 1);
        
        // Show disconnect button
        if (wifi_state.disconnect_button) {
            gtk_widget_set_visible(wifi_state.disconnect_button, TRUE);
        }
        
        g_free(status_text);
    } else {
        gtk_label_set_text(GTK_LABEL(status_label), "Not connected to any network");
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

// Refresh the WiFi network list
static void refresh_wifi_list(GtkWidget *button, gpointer user_data) {
    GtkWidget *listbox = wifi_state.network_list;
    if (!listbox || !GTK_IS_LIST_BOX(listbox)) {
        return;
    }
    
    // Prevent multiple refreshes at once
    if (wifi_state.is_refreshing) {
        return;
    }
    wifi_state.is_refreshing = true;
    
    // Disable refresh button during refresh
    if (wifi_state.refresh_button) {
        gtk_widget_set_sensitive(wifi_state.refresh_button, FALSE);
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
        
        // Re-enable refresh button
        if (wifi_state.refresh_button) {
            gtk_widget_set_sensitive(wifi_state.refresh_button, TRUE);
        }
        
        wifi_state.is_refreshing = false;
        return;
    }
    
    // Get current connection
    char *current_connection = get_current_connection();
    
    // Get WiFi list with more details
    char *output = execute_command("nmcli -t -f SSID,SIGNAL,SECURITY device wifi list");
    if (!output) {
        // Add a message if no networks found
        GtkWidget *row = gtk_list_box_row_new();
        GtkWidget *label = gtk_label_new("No networks found");
        gtk_list_box_row_set_child(GTK_LIST_BOX_ROW(row), label);
        gtk_list_box_append(GTK_LIST_BOX(listbox), row);
        
        if (current_connection) free(current_connection);
        
        // Re-enable refresh button
        if (wifi_state.refresh_button) {
            gtk_widget_set_sensitive(wifi_state.refresh_button, TRUE);
        }
        
        wifi_state.is_refreshing = false;
        return;
    }
    
    // Parse and add networks
    char *saveptr;
    char *line = strtok_r(output, "\n", &saveptr);
    int networks_added = 0;
    
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
            }
            
            // Create and add the row
            GtkWidget *row = create_wifi_row(line, signal, is_connected);
            gtk_list_box_append(GTK_LIST_BOX(listbox), row);
            networks_added++;
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
    
    free(output);
    if (current_connection) free(current_connection);
    
    // Re-enable refresh button
    if (wifi_state.refresh_button) {
        gtk_widget_set_sensitive(wifi_state.refresh_button, TRUE);
    }
    
    wifi_state.is_refreshing = false;
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
    GtkWidget *dialog = gtk_message_dialog_new(GTK_WINDOW(gtk_widget_get_root(parent)),
                                             GTK_DIALOG_MODAL | GTK_DIALOG_DESTROY_WITH_PARENT,
                                             GTK_MESSAGE_ERROR,
                                             GTK_BUTTONS_OK,
                                             "WiFi Connection Error");
    
    gtk_message_dialog_format_secondary_text(GTK_MESSAGE_DIALOG(dialog), "%s", error_message);
    gtk_window_set_title(GTK_WINDOW(dialog), "Connection Error");
    
    g_signal_connect_swapped(dialog, "response", G_CALLBACK(gtk_window_destroy), dialog);
    gtk_window_present(GTK_WINDOW(dialog));
}

// Connect to a WiFi network
static void connect_wifi(GtkListBoxRow *row, gpointer user_data) {
    GtkWidget *network_list = GTK_WIDGET(user_data);
    GtkWidget *parent_window = gtk_widget_get_toplevel(network_list);
    
    // Get the selected network SSID
    GtkWidget *ssid_label = gtk_bin_get_child(GTK_BIN(row));
    const char *ssid = gtk_label_get_text(GTK_LABEL(ssid_label));
    
    // Show confirmation dialog
    GtkWidget *dialog = gtk_message_dialog_new(
        GTK_WINDOW(parent_window),
        GTK_DIALOG_MODAL,
        GTK_MESSAGE_QUESTION,
        GTK_BUTTONS_YES_NO,
        "Connect to network '%s'?", ssid
    );
    
    int response = gtk_dialog_run(GTK_DIALOG(dialog));
    gtk_widget_destroy(dialog);
    
    if (response == GTK_RESPONSE_YES) {
        // Proceed with connection
        char command[256];
        snprintf(command, sizeof(command), "nmcli device wifi connect '%s'", ssid);
        char *output = execute_command(command);
        
        if (output && strstr(output, "successfully")) {
            update_connection_status(wifi_state.status_label);
        } else {
            show_connection_error(parent_window, "Failed to connect to network");
        }
        
        if (output) free(output);
    }
}

// Handler for WiFi connect button click
static void on_wifi_connect_clicked(GtkWidget *button, gpointer user_data) {
    GtkWidget *dialog = GTK_WIDGET(g_object_get_data(G_OBJECT(button), "dialog"));
    GtkWidget *entry = GTK_WIDGET(g_object_get_data(G_OBJECT(button), "password_entry"));
    const char *ssid = g_object_get_data(G_OBJECT(button), "ssid");
    
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
    g_signal_connect(wifi_list, "row-activated", G_CALLBACK(connect_wifi), wifi_list);
    g_signal_connect(refresh_button, "clicked", G_CALLBACK(refresh_wifi_list), NULL);
    
    // Set initial status
    update_connection_status(status_label);
    
    // Initial refresh of network list
    refresh_wifi_list(NULL, NULL);
} 