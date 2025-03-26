use gtk::prelude::*;  // Importação do prelude para facilitar o uso de GTK

fn main() {
    gtk::init().unwrap();  // Inicializa o GTK
    let window = gtk::Window::new(gtk::WindowType::Toplevel);  // Cria uma nova janela
    window.set_title("Hi!");  // Define o título da janela
    window.set_default_size(200, 100);  // Tamanho padrão da janela
    window.set_position(gtk::WindowPosition::Center);  // Centraliza a janela

    let label = gtk::Label::new(Some("Hi!"));  // Cria um rótulo com o texto "Hi!"
    window.add(&label);  // Adiciona o rótulo à janela

    window.show_all();  // Exibe a janela e todos os widgets

    // Conecta o evento de fechar a janela ao término do programa
    window.connect_delete_event(|_, _| {
        gtk::main_quit();
        gtk::Inhibit(false)  // Permite fechar a janela
    });

    gtk::main();  // Inicia o loop de eventos
}
