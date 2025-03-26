#include "better_control.h"
#include <gtk/gtk.h>

void set_brightness(int brightness) {
    char *cmd = g_strdup_printf("brightnessctl set %d%%", brightness);
    char *output = execute_command(cmd);
    g_free(cmd);
    if (output) {
        free(output);
    }
}

static void on_brightness_changed(GtkWidget *scale, gpointer user_data G_GNUC_UNUSED) {
    int brightness = (int)gtk_range_get_value(GTK_RANGE(scale));
    set_brightness(brightness);
}

static void set_brightness_percentage(GtkWidget *button G_GNUC_UNUSED, int percentage) {
    set_brightness(percentage);
}

void init_brightness_page(GtkWidget *notebook, AppState *state G_GNUC_UNUSED) {
    GtkWidget *brightness_box = gtk_box_new(GTK_ORIENTATION_VERTICAL, 10);
    gtk_widget_set_margin_top(brightness_box, 10);
    gtk_widget_set_margin_bottom(brightness_box, 10);
    gtk_widget_set_margin_start(brightness_box, 10);
    gtk_widget_set_margin_end(brightness_box, 10);
    
    // Create grid for layout
    GtkWidget *grid = gtk_grid_new();
    gtk_grid_set_column_homogeneous(GTK_GRID(grid), TRUE);
    gtk_grid_set_row_homogeneous(GTK_GRID(grid), TRUE);
    gtk_grid_set_column_spacing(GTK_GRID(grid), 10);
    gtk_grid_set_row_spacing(GTK_GRID(grid), 10);
    gtk_box_append(GTK_BOX(brightness_box), grid);
    
    // Brightness label
    GtkWidget *brightness_label = gtk_label_new("Screen Brightness");
    gtk_label_set_xalign(GTK_LABEL(brightness_label), 0);
    gtk_grid_attach(GTK_GRID(grid), brightness_label, 0, 0, 5, 1);
    
    // Brightness scale
    GtkWidget *brightness_scale = gtk_scale_new_with_range(GTK_ORIENTATION_HORIZONTAL, 0, 100, 1);
    gtk_range_set_value(GTK_RANGE(brightness_scale), get_current_brightness());
    gtk_scale_set_value_pos(GTK_SCALE(brightness_scale), GTK_POS_LEFT);
    g_signal_connect(brightness_scale, "value-changed", G_CALLBACK(on_brightness_changed), NULL);
    gtk_grid_attach(GTK_GRID(grid), brightness_scale, 0, 1, 5, 1);
    
    // Brightness percentage buttons
    for (int i = 0; i < 5; i++) {
        int percentage = i * 25;
        GtkWidget *button = gtk_button_new_with_label(g_strdup_printf("%d%%", percentage));
        g_signal_connect(button, "clicked", G_CALLBACK(set_brightness_percentage), GINT_TO_POINTER(percentage));
        gtk_grid_attach(GTK_GRID(grid), button, i, 2, 1, 1);
    }
    
    // Create scrolled window
    GtkWidget *scrolled = gtk_scrolled_window_new();
    gtk_scrolled_window_set_policy(GTK_SCROLLED_WINDOW(scrolled),
                                 GTK_POLICY_AUTOMATIC,
                                 GTK_POLICY_AUTOMATIC);
    gtk_scrolled_window_set_child(GTK_SCROLLED_WINDOW(scrolled), brightness_box);
    
    // Add to notebook
    GtkWidget *label = gtk_label_new("Brightness");
    gtk_notebook_append_page(GTK_NOTEBOOK(notebook), scrolled, label);
} 