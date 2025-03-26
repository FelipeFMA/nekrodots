#include "better_control.h"

static void refresh_bluetooth_list(GtkWidget *listbox) {
    // Clear existing items
    GtkWidget *child = gtk_widget_get_first_child(listbox);
    while (child) {
        GtkWidget *next = gtk_widget_get_next_sibling(child);
        gtk_list_box_remove(GTK_LIST_BOX(listbox), child);
        child = next;
    }
    
    // Get Bluetooth devices using bluetoothctl
    char *output = execute_command("bluetoothctl devices");
    if (!output) return;
    
    char *line = strtok(output, "\n");
    while (line) {
        char *mac = strtok(line, " ");
        char *name = strtok(NULL, " ");
        
        if (name) {
            GtkWidget *row = gtk_list_box_row_new();
            GtkWidget *box = gtk_box_new(GTK_ORIENTATION_HORIZONTAL, 5);
            
            GtkWidget *name_label = gtk_label_new(name);
            GtkWidget *mac_label = gtk_label_new(mac);
            
            gtk_box_append(GTK_BOX(box), name_label);
            gtk_box_append(GTK_BOX(box), mac_label);
            
            // Add connect/disconnect buttons
            GtkWidget *button_box = gtk_box_new(GTK_ORIENTATION_HORIZONTAL, 5);
            
            GtkWidget *connect_button = gtk_button_new_with_label("Connect");
            g_signal_connect(connect_button, "clicked", G_CALLBACK(connect_bluetooth_device), mac);
            gtk_box_append(GTK_BOX(button_box), connect_button);
            
            GtkWidget *disconnect_button = gtk_button_new_with_label("Disconnect");
            g_signal_connect(disconnect_button, "clicked", G_CALLBACK(disconnect_bluetooth_device), mac);
            gtk_box_append(GTK_BOX(button_box), disconnect_button);
            
            gtk_box_append(GTK_BOX(box), button_box);
            
            gtk_list_box_row_set_child(GTK_LIST_BOX_ROW(row), box);
            gtk_list_box_append(GTK_LIST_BOX(listbox), row);
        }
        
        line = strtok(NULL, "\n");
    }
    
    free(output);
}

static void enable_bluetooth(GtkWidget *button, gpointer user_data) {
    char *output = execute_command("bluetoothctl power on");
    if (output) {
        show_error_dialog(GTK_WIDGET(gtk_widget_get_root(button)), output);
        free(output);
    }
    refresh_bluetooth_list(GTK_WIDGET(user_data));
}

static void disable_bluetooth(GtkWidget *button, gpointer user_data) {
    char *output = execute_command("bluetoothctl power off");
    if (output) {
        show_error_dialog(GTK_WIDGET(gtk_widget_get_root(button)), output);
        free(output);
    }
    refresh_bluetooth_list(GTK_WIDGET(user_data));
}

void connect_bluetooth_device(GtkWidget *button, const char *mac) {
    char *cmd = g_strdup_printf("bluetoothctl connect %s", mac);
    char *output = execute_command(cmd);
    g_free(cmd);
    
    if (output) {
        show_error_dialog(GTK_WIDGET(gtk_widget_get_root(button)), output);
        free(output);
    }
}

void disconnect_bluetooth_device(GtkWidget *button, const char *mac) {
    char *cmd = g_strdup_printf("bluetoothctl disconnect %s", mac);
    char *output = execute_command(cmd);
    g_free(cmd);
    
    if (output) {
        show_error_dialog(GTK_WIDGET(gtk_widget_get_root(button)), output);
        free(output);
    }
}

void init_bluetooth_page(GtkWidget *notebook, AppState *state G_GNUC_UNUSED) {
    GtkWidget *bluetooth_box = gtk_box_new(GTK_ORIENTATION_VERTICAL, 10);
    gtk_widget_set_margin_top(bluetooth_box, 10);
    gtk_widget_set_margin_bottom(bluetooth_box, 10);
    gtk_widget_set_margin_start(bluetooth_box, 10);
    gtk_widget_set_margin_end(bluetooth_box, 10);
    
    // Create Bluetooth list
    GtkWidget *bt_listbox = gtk_list_box_new();
    gtk_list_box_set_selection_mode(GTK_LIST_BOX(bt_listbox), GTK_SELECTION_SINGLE);
    gtk_box_append(GTK_BOX(bluetooth_box), bt_listbox);
    
    // Create button box
    GtkWidget *button_box = gtk_box_new(GTK_ORIENTATION_HORIZONTAL, 5);
    
    GtkWidget *enable_button = gtk_button_new_with_label("Enable Bluetooth");
    g_signal_connect(enable_button, "clicked", G_CALLBACK(enable_bluetooth), bt_listbox);
    gtk_box_append(GTK_BOX(button_box), enable_button);
    
    GtkWidget *disable_button = gtk_button_new_with_label("Disable Bluetooth");
    g_signal_connect(disable_button, "clicked", G_CALLBACK(disable_bluetooth), bt_listbox);
    gtk_box_append(GTK_BOX(button_box), disable_button);
    
    GtkWidget *refresh_button = gtk_button_new_with_label("Refresh Devices");
    g_signal_connect(refresh_button, "clicked", G_CALLBACK(refresh_bluetooth_list), bt_listbox);
    gtk_box_append(GTK_BOX(button_box), refresh_button);
    
    // Add button box to the bottom
    gtk_box_append(GTK_BOX(bluetooth_box), button_box);
    
    // Create scrolled window
    GtkWidget *scrolled = gtk_scrolled_window_new();
    gtk_scrolled_window_set_policy(GTK_SCROLLED_WINDOW(scrolled),
                                 GTK_POLICY_AUTOMATIC,
                                 GTK_POLICY_AUTOMATIC);
    gtk_scrolled_window_set_child(GTK_SCROLLED_WINDOW(scrolled), bluetooth_box);
    
    // Add to notebook
    GtkWidget *label = gtk_label_new("Bluetooth");
    gtk_notebook_append_page(GTK_NOTEBOOK(notebook), scrolled, label);
    
    // Initial refresh
    refresh_bluetooth_list(bt_listbox);
} 