#include "better_control.h"
#include <gtk/gtk.h>

void set_volume(int volume) {
    char *cmd = g_strdup_printf("pactl set-sink-volume @DEFAULT_SINK@ %d%%", volume);
    char *output = execute_command(cmd);
    g_free(cmd);
    if (output) {
        free(output);
    }
}

void set_mic_volume(int volume) {
    char *cmd = g_strdup_printf("pactl set-source-volume @DEFAULT_SOURCE@ %d%%", volume);
    char *output = execute_command(cmd);
    g_free(cmd);
    if (output) {
        free(output);
    }
}

static void on_volume_changed(GtkWidget *scale, gpointer user_data G_GNUC_UNUSED) {
    int volume = (int)gtk_range_get_value(GTK_RANGE(scale));
    set_volume(volume);
}

static void on_mic_volume_changed(GtkWidget *scale, gpointer user_data G_GNUC_UNUSED) {
    int volume = (int)gtk_range_get_value(GTK_RANGE(scale));
    set_mic_volume(volume);
}

static void mute_speaker(GtkWidget *button, gpointer user_data G_GNUC_UNUSED) {
    char *output = execute_command("pactl get-sink-mute @DEFAULT_SINK@");
    if (!output) return;
    
    int is_muted = strstr(output, "yes") != NULL;
    char *cmd = g_strdup_printf("pactl set-sink-mute @DEFAULT_SINK@ %s", is_muted ? "0" : "1");
    char *cmd_output = execute_command(cmd);
    g_free(cmd);
    free(output);
    if (cmd_output) {
        free(cmd_output);
    }
    
    gtk_button_set_label(GTK_BUTTON(button), is_muted ? "Mute Speaker" : "Unmute Speaker");
}

static void mute_mic(GtkWidget *button, gpointer user_data G_GNUC_UNUSED) {
    char *output = execute_command("pactl get-source-mute @DEFAULT_SOURCE@");
    if (!output) return;
    
    int is_muted = strstr(output, "yes") != NULL;
    char *cmd = g_strdup_printf("pactl set-source-mute @DEFAULT_SOURCE@ %s", is_muted ? "0" : "1");
    char *cmd_output = execute_command(cmd);
    g_free(cmd);
    free(output);
    if (cmd_output) {
        free(cmd_output);
    }
    
    gtk_button_set_label(GTK_BUTTON(button), is_muted ? "Mute Mic" : "Unmute Mic");
}

static void set_volume_percentage(GtkWidget *button G_GNUC_UNUSED, int percentage) {
    set_volume(percentage);
}

static void set_mic_percentage(GtkWidget *button G_GNUC_UNUSED, int percentage) {
    set_mic_volume(percentage);
}

void init_audio_page(GtkWidget *notebook, AppState *state G_GNUC_UNUSED) {
    GtkWidget *audio_box = gtk_box_new(GTK_ORIENTATION_VERTICAL, 10);
    gtk_widget_set_margin_top(audio_box, 10);
    gtk_widget_set_margin_bottom(audio_box, 10);
    gtk_widget_set_margin_start(audio_box, 10);
    gtk_widget_set_margin_end(audio_box, 10);
    
    // Create grid for layout
    GtkWidget *grid = gtk_grid_new();
    gtk_grid_set_column_homogeneous(GTK_GRID(grid), TRUE);
    gtk_grid_set_row_homogeneous(GTK_GRID(grid), TRUE);
    gtk_grid_set_column_spacing(GTK_GRID(grid), 10);
    gtk_grid_set_row_spacing(GTK_GRID(grid), 10);
    gtk_box_append(GTK_BOX(audio_box), grid);
    
    // Speaker controls
    GtkWidget *speaker_label = gtk_label_new("Speaker Volume");
    gtk_label_set_xalign(GTK_LABEL(speaker_label), 0);
    gtk_grid_attach(GTK_GRID(grid), speaker_label, 0, 0, 5, 1);
    
    GtkWidget *speaker_scale = gtk_scale_new_with_range(GTK_ORIENTATION_HORIZONTAL, 0, 100, 1);
    gtk_range_set_value(GTK_RANGE(speaker_scale), get_current_volume());
    gtk_scale_set_value_pos(GTK_SCALE(speaker_scale), GTK_POS_LEFT);
    g_signal_connect(speaker_scale, "value-changed", G_CALLBACK(on_volume_changed), NULL);
    gtk_grid_attach(GTK_GRID(grid), speaker_scale, 0, 1, 5, 1);
    
    // Speaker percentage buttons
    for (int i = 0; i < 5; i++) {
        int percentage = i * 25;
        GtkWidget *button = gtk_button_new_with_label(g_strdup_printf("%d%%", percentage));
        g_signal_connect(button, "clicked", G_CALLBACK(set_volume_percentage), GINT_TO_POINTER(percentage));
        gtk_grid_attach(GTK_GRID(grid), button, i, 2, 1, 1);
    }
    
    // Microphone controls
    GtkWidget *mic_label = gtk_label_new("Microphone Volume");
    gtk_label_set_xalign(GTK_LABEL(mic_label), 0);
    gtk_grid_attach(GTK_GRID(grid), mic_label, 0, 3, 5, 1);
    
    GtkWidget *mic_scale = gtk_scale_new_with_range(GTK_ORIENTATION_HORIZONTAL, 0, 100, 1);
    gtk_range_set_value(GTK_RANGE(mic_scale), get_current_mic_volume());
    gtk_scale_set_value_pos(GTK_SCALE(mic_scale), GTK_POS_LEFT);
    g_signal_connect(mic_scale, "value-changed", G_CALLBACK(on_mic_volume_changed), NULL);
    gtk_grid_attach(GTK_GRID(grid), mic_scale, 0, 4, 5, 1);
    
    // Microphone percentage buttons
    for (int i = 0; i < 5; i++) {
        int percentage = i * 25;
        GtkWidget *button = gtk_button_new_with_label(g_strdup_printf("%d%%", percentage));
        g_signal_connect(button, "clicked", G_CALLBACK(set_mic_percentage), GINT_TO_POINTER(percentage));
        gtk_grid_attach(GTK_GRID(grid), button, i, 5, 1, 1);
    }
    
    // Mute buttons
    GtkWidget *speaker_mute = gtk_button_new_with_label("Mute Speaker");
    g_signal_connect(speaker_mute, "clicked", G_CALLBACK(mute_speaker), NULL);
    gtk_grid_attach(GTK_GRID(grid), speaker_mute, 0, 6, 1, 1);
    
    GtkWidget *mic_mute = gtk_button_new_with_label("Mute Mic");
    g_signal_connect(mic_mute, "clicked", G_CALLBACK(mute_mic), NULL);
    gtk_grid_attach(GTK_GRID(grid), mic_mute, 1, 6, 1, 1);
    
    // Create scrolled window
    GtkWidget *scrolled = gtk_scrolled_window_new();
    gtk_scrolled_window_set_policy(GTK_SCROLLED_WINDOW(scrolled),
                                 GTK_POLICY_AUTOMATIC,
                                 GTK_POLICY_AUTOMATIC);
    gtk_scrolled_window_set_child(GTK_SCROLLED_WINDOW(scrolled), audio_box);
    
    // Add to notebook
    GtkWidget *label = gtk_label_new("Audio");
    gtk_notebook_append_page(GTK_NOTEBOOK(notebook), scrolled, label);
} 