#include "better_control.h"
#include <getopt.h>

// Function to set up CSS to fix GTK warnings
static void setup_css(void) {
    GtkCssProvider *provider = gtk_css_provider_new();
    gtk_css_provider_load_from_string(provider,
        "image { min-width: 16px; min-height: 16px; }");
    
    GdkDisplay *display = gdk_display_get_default();
    gtk_style_context_add_provider_for_display(display,
        GTK_STYLE_PROVIDER(provider),
        GTK_STYLE_PROVIDER_PRIORITY_APPLICATION);
    
    g_object_unref(provider);
}

// Function to switch to a specific tab
static void switch_to_tab(GtkNotebook *notebook, int tab_index) {
    if (notebook && tab_index >= 0 && tab_index < gtk_notebook_get_n_pages(notebook)) {
        gtk_notebook_set_current_page(notebook, tab_index);
    }
}

// Print help message
static void print_help(const char *program_name) {
    printf("Usage: %s [OPTIONS]\n\n", program_name);
    printf("Options:\n");
    printf("  -w, --wifi        Open directly to WiFi tab\n");
    printf("  -b, --bluetooth   Open directly to Bluetooth tab\n");
    printf("  -a, --audio       Open directly to Audio tab\n");
    printf("  -r, --brightness  Open directly to Brightness tab\n");
    printf("  -h, --help        Display this help and exit\n");
}

static void activate(GtkApplication *app, gpointer user_data) {
    AppState *state = g_new(AppState, 1);
    
    // Get the tab index from user_data
    int tab_index = GPOINTER_TO_INT(user_data);
    
    // Set up CSS to fix GTK warnings
    setup_css();
    
    // Create main window
    state->window = gtk_application_window_new(app);
    gtk_window_set_title(GTK_WINDOW(state->window), "Better Control");
    gtk_window_set_default_size(GTK_WINDOW(state->window), 1000, 700);
    gtk_window_set_resizable(GTK_WINDOW(state->window), TRUE);
    
    // Create main container
    GtkWidget *main_container = gtk_box_new(GTK_ORIENTATION_VERTICAL, 10);
    gtk_window_set_child(GTK_WINDOW(state->window), main_container);
    
    // Create notebook
    state->notebook = gtk_notebook_new();
    gtk_notebook_set_scrollable(GTK_NOTEBOOK(state->notebook), TRUE);
    gtk_box_append(GTK_BOX(main_container), state->notebook);
    
    // Initialize pages
    init_wifi_page(state->notebook, state);
    init_bluetooth_page(state->notebook, state);
    init_audio_page(state->notebook, state);
    init_brightness_page(state->notebook, state);
    
    // Switch to the specified tab if needed
    if (tab_index >= 0) {
        switch_to_tab(GTK_NOTEBOOK(state->notebook), tab_index);
    }
    
    // Present the window instead of using deprecated gtk_widget_show
    gtk_window_present(GTK_WINDOW(state->window));
}

int main(int argc, char **argv) {
    GtkApplication *app;
    int status;
    int tab_index = -1; // Default: no specific tab
    
    // Define long options
    static struct option long_options[] = {
        {"wifi",       no_argument, 0, 'w'},
        {"bluetooth",  no_argument, 0, 'b'},
        {"audio",      no_argument, 0, 'a'},
        {"brightness", no_argument, 0, 'r'},
        {"help",       no_argument, 0, 'h'},
        {0, 0, 0, 0}
    };
    
    // Parse command line options
    int opt;
    int option_index = 0;
    
    while ((opt = getopt_long(argc, argv, "wbarh", long_options, &option_index)) != -1) {
        switch (opt) {
            case 'w': // WiFi
                tab_index = 0;
                break;
            case 'b': // Bluetooth
                tab_index = 1;
                break;
            case 'a': // Audio
                tab_index = 2;
                break;
            case 'r': // Brightness (using 'r' since 'b' is already used)
                tab_index = 3;
                break;
            case 'h': // Help
                print_help(argv[0]);
                return 0;
            default:
                fprintf(stderr, "Try '%s --help' for more information.\n", argv[0]);
                return 1;
        }
    }
    
    // Use G_APPLICATION_DEFAULT_FLAGS instead of deprecated G_APPLICATION_FLAGS_NONE
    app = gtk_application_new("org.gtk.better-control", G_APPLICATION_DEFAULT_FLAGS);
    g_signal_connect(app, "activate", G_CALLBACK(activate), GINT_TO_POINTER(tab_index));
    status = g_application_run(G_APPLICATION(app), 1, argv); // Use 1 for argc to prevent GTK from parsing our args
    g_object_unref(app);
    
    return status;
}