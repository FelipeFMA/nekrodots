#include <gtk/gtk.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

// Widgets
GtkWidget *window;
GtkWidget *grid;
GtkWidget *display;
GtkWidget *buttons[20];

// Calculator state
char display_text[256] = "0";
double first_operand = 0.0;
double second_operand = 0.0;
char operation = '\0';
gboolean new_input = TRUE;
gboolean has_decimal = FALSE;

// Function prototypes
static void update_display();
static void clear_calculator();
static void button_clicked(GtkWidget *widget, gpointer data);
static void calculate_result();

// Update the display with the current text
static void update_display() {
    gtk_label_set_text(GTK_LABEL(display), display_text);
}

// Clear calculator state
static void clear_calculator() {
    strcpy(display_text, "0");
    first_operand = 0.0;
    second_operand = 0.0;
    operation = '\0';
    new_input = TRUE;
    has_decimal = FALSE;
    update_display();
}

// Calculate the result based on the operation
static void calculate_result() {
    second_operand = atof(display_text);
    double result = 0.0;
    
    switch (operation) {
        case '+':
            result = first_operand + second_operand;
            break;
        case '-':
            result = first_operand - second_operand;
            break;
        case '*':
            result = first_operand * second_operand;
            break;
        case '/':
            if (second_operand != 0) {
                result = first_operand / second_operand;
            } else {
                strcpy(display_text, "Error");
                update_display();
                return;
            }
            break;
    }
    
    // Convert result to string
    snprintf(display_text, sizeof(display_text), "%.10g", result);
    
    // Reset calculator state
    first_operand = result;
    operation = '\0';
    new_input = TRUE;
    has_decimal = (strchr(display_text, '.') != NULL);
    
    update_display();
}

// Button click handler
static void button_clicked(GtkWidget *widget, gpointer data) {
    const char *button_text = (const char *)data;
    
    // Handle numeric buttons (0-9)
    if ((button_text[0] >= '0' && button_text[0] <= '9') || (button_text[0] == '.' && !has_decimal)) {
        if (new_input) {
            if (button_text[0] == '.') {
                strcpy(display_text, "0.");
                has_decimal = TRUE;
            } else {
                strcpy(display_text, button_text);
            }
            new_input = FALSE;
        } else {
            // Don't allow multiple decimal points
            if (button_text[0] == '.') {
                has_decimal = TRUE;
            }
            
            // Append digit if not already too long
            if (strlen(display_text) < sizeof(display_text) - 2) {
                strcat(display_text, button_text);
            }
        }
        update_display();
        return;
    }
    
    // Handle operation buttons (+, -, *, /)
    if (button_text[0] == '+' || button_text[0] == '-' || 
        button_text[0] == '*' || button_text[0] == '/') {
        
        // If we already have an operation pending, calculate it first
        if (operation != '\0' && !new_input) {
            calculate_result();
        } else {
            first_operand = atof(display_text);
        }
        
        operation = button_text[0];
        new_input = TRUE;
        has_decimal = FALSE;
        return;
    }
    
    // Handle equals button
    if (button_text[0] == '=') {
        if (operation != '\0') {
            calculate_result();
        }
        return;
    }
    
    // Handle clear button
    if (strcmp(button_text, "C") == 0) {
        clear_calculator();
        return;
    }
    
    // Handle backspace button
    if (strcmp(button_text, "⌫") == 0) {
        int len = strlen(display_text);
        if (len > 0) {
            // Check if we're removing a decimal point
            if (display_text[len - 1] == '.') {
                has_decimal = FALSE;
            }
            
            // Remove the last character
            display_text[len - 1] = '\0';
            
            // If we've deleted everything, show 0
            if (len == 1 || strlen(display_text) == 0) {
                strcpy(display_text, "0");
                new_input = TRUE;
            }
            
            update_display();
        }
        return;
    }
}

// Window close handler
static void on_window_destroy(GtkWidget *widget, gpointer data) {
    gtk_main_quit();
}

int main(int argc, char *argv[]) {
    // Initialize GTK
    gtk_init(&argc, &argv);
    
    // Create the main window
    window = gtk_window_new(GTK_WINDOW_TOPLEVEL);
    gtk_window_set_title(GTK_WINDOW(window), "GTK Calculator");
    gtk_window_set_default_size(GTK_WINDOW(window), 300, 300);
    gtk_window_set_position(GTK_WINDOW(window), GTK_WIN_POS_CENTER);
    gtk_container_set_border_width(GTK_CONTAINER(window), 10);
    gtk_window_set_resizable(GTK_WINDOW(window), FALSE);
    g_signal_connect(window, "destroy", G_CALLBACK(on_window_destroy), NULL);
    
    // Create a grid layout
    grid = gtk_grid_new();
    gtk_grid_set_row_spacing(GTK_GRID(grid), 5);
    gtk_grid_set_column_spacing(GTK_GRID(grid), 5);
    gtk_container_add(GTK_CONTAINER(window), grid);
    
    // Create the display
    display = gtk_label_new("0");
    gtk_widget_set_hexpand(display, TRUE);
    gtk_label_set_xalign(GTK_LABEL(display), 1.0);  // Right-align text
    gtk_widget_set_margin_bottom(display, 10);
    
    // Set display font and size
    PangoAttrList *attr_list = pango_attr_list_new();
    PangoAttribute *attr = pango_attr_size_new(24 * PANGO_SCALE);
    pango_attr_list_insert(attr_list, attr);
    gtk_label_set_attributes(GTK_LABEL(display), attr_list);
    pango_attr_list_unref(attr_list);
    
    // Add the display to the grid (spanning all 4 columns)
    gtk_grid_attach(GTK_GRID(grid), display, 0, 0, 4, 1);
    
    // Button labels
    const char *button_labels[] = {
        "7", "8", "9", "/",
        "4", "5", "6", "*",
        "1", "2", "3", "-",
        "0", ".", "=", "+",
        "C", "⌫"
    };
    
    // Create and add buttons to the grid
    int row, col;
    int button_index = 0;
    
    for (row = 1; row <= 5; row++) {
        for (col = 0; col < 4; col++) {
            // Skip the last two positions in the grid
            if (row == 5 && col > 1) {
                continue;
            }
            
            buttons[button_index] = gtk_button_new_with_label(button_labels[button_index]);
            gtk_widget_set_hexpand(buttons[button_index], TRUE);
            gtk_widget_set_vexpand(buttons[button_index], TRUE);
            
            // Make the C and backspace buttons span 2 columns
            if (row == 5) {
                gtk_grid_attach(GTK_GRID(grid), buttons[button_index], col * 2, row, 2, 1);
            } else {
                gtk_grid_attach(GTK_GRID(grid), buttons[button_index], col, row, 1, 1);
            }
            
            g_signal_connect(buttons[button_index], "clicked", 
                            G_CALLBACK(button_clicked), 
                            (gpointer)button_labels[button_index]);
            
            button_index++;
        }
    }
    
    // Show all widgets
    gtk_widget_show_all(window);
    
    // Start the GTK main loop
    gtk_main();
    
    return 0;
}
