#include <gtk/gtk.h>
#include <glib.h>
#include <stdlib.h>
#include <string.h>

// Function to get the current shell
char *get_shell() {
    char *shell = getenv("SHELL");
    if (shell == NULL) {
        shell = (char *)malloc(10 * sizeof(char));
        strcpy(shell, "/bin/bash");
    }
    return shell;
}

// Function to execute a command
void execute_command(char *command) {
    char *shell = get_shell();
    char cmd[256];
    sprintf(cmd, "%s -c \"%s\"", shell, command);
    system(cmd);
}

// Callback function for sound settings
void on_sound_settings_clicked(GtkButton *button, gpointer user_data) {
    execute_command("pavucontrol");
}

// Callback function for WiFi settings
void on_wifi_settings_clicked(GtkButton *button, gpointer user_data) {
    execute_command("nm-connection-editor");
}

// Callback function for Bluetooth settings
void on_bluetooth_settings_clicked(GtkButton *button, gpointer user_data) {
    execute_command("blueman-applet");
}

int main(int argc, char *argv[]) {
    // Initialize GTK
    gtk_init(&argc, &argv);

    // Create main window
    GtkWidget *window = gtk_window_new(GTK_WINDOW_TOPLEVEL);
    gtk_window_set_title(GTK_WINDOW(window), "HyprControl");
    gtk_window_set_default_size(GTK_WINDOW(window), 400, 300);

    // Create a vertical box container
    GtkWidget *vbox = gtk_box_new(GTK_ORIENTATION_VERTICAL, 10);
    gtk_widget_set_margin_start(vbox, 10);
    gtk_widget_set_margin_end(vbox, 10);
    gtk_widget_set_margin_top(vbox, 10);
    gtk_widget_set_margin_bottom(vbox, 10);
    gtk_container_add(GTK_CONTAINER(window), vbox);

    // Create sound settings button
    GtkWidget *sound_button = gtk_button_new_with_label("Configurar Som");
    g_signal_connect(sound_button, "clicked", G_CALLBACK(on_sound_settings_clicked), NULL);
    gtk_box_pack_start(GTK_BOX(vbox), sound_button, FALSE, FALSE, 0);

    // Create WiFi settings button
    GtkWidget *wifi_button = gtk_button_new_with_label("Configurar WiFi");
    g_signal_connect(wifi_button, "clicked", G_CALLBACK(on_wifi_settings_clicked), NULL);
    gtk_box_pack_start(GTK_BOX(vbox), wifi_button, FALSE, FALSE, 0);

    // Create Bluetooth settings button
    GtkWidget *bluetooth_button = gtk_button_new_with_label("Configurar Bluetooth");
    g_signal_connect(bluetooth_button, "clicked", G_CALLBACK(on_bluetooth_settings_clicked), NULL);
    gtk_box_pack_start(GTK_BOX(vbox), bluetooth_button, FALSE, FALSE, 0);

    // Show all widgets
    gtk_widget_show_all(window);

    // Start the GTK main loop
    gtk_main();

    return 0;
}
