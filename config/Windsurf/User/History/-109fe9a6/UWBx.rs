mod wayland;
mod utils;

use anyhow::Result;
use clap::Parser;
use tracing::{info, error, debug};
use tokio::runtime::Runtime;
use std::time::Duration;
use dirs;

#[derive(Parser, Debug)]
#[command(author, version, about, long_about = None)]
struct Args {
    /// Output file path
    #[arg(short, long, default_value_t = default_screenshot_path())]
    output: String,
    
    /// Timeout in seconds for screenshot capture
    #[arg(short, long, default_value = "5")]
    timeout: u64,
}

fn default_screenshot_path() -> String {
    // Get the user's pictures directory from XDG specification
    let pictures_dir = dirs::picture_dir().unwrap_or_else(|| {
        error!("Could not find XDG pictures directory, using current directory");
        std::path::PathBuf::from(".")
    });
    
    let screenshots_dir = pictures_dir.join("Screenshots");
    
    // Create directory if it doesn't exist
    std::fs::create_dir_all(&screenshots_dir).unwrap_or_else(|_| {
        error!("Failed to create screenshots directory: {}", screenshots_dir.display());
    });
    
    // Generate a filename with timestamp
    let now = chrono::Local::now();
    let timestamp = now.format("%Y-%m-%d_%H-%M-%S");
    format!("{}/screenshot_{}.png", screenshots_dir.display(), timestamp)
}

fn main() -> Result<()> {
    // Initialize tracing
    tracing_subscriber::fmt::init();
    
    info!("Starting NekroShot");
    
    let args = Args::parse();
    info!("Screenshot will be saved to: {}", args.output);
    
    // Create a Tokio runtime
    let rt = Runtime::new()?;
    
    // Capture screenshot with timeout
    let result = rt.block_on(async {
        debug!("Starting screenshot capture");
        
        // Create a timeout future
        let timeout_future = tokio::time::sleep(Duration::from_secs(args.timeout));
        let capture_future = wayland::capture_screenshot();
        
        // Race the futures
        let result = tokio::select! {
            img = capture_future => img,
            _ = timeout_future => {
                error!("Screenshot capture timed out after {} seconds", args.timeout);
                Err(anyhow::anyhow!("Screenshot capture timed out"))
            }
        };
        
        match result {
            Ok(img) => {
                debug!("Screenshot captured successfully: {}x{}", img.width(), img.height());
                
                debug!("Saving image to {}", args.output);
                // Save the image
                if let Err(e) = img.save(&args.output) {
                    error!("Failed to save image: {}", e);
                    return Err(e.into());
                }
                info!("Screenshot saved to: {}", args.output);
                
                Ok(())
            },
            Err(e) => {
                error!("Failed to capture screenshot: {}", e);
                Err(e)
            }
        }
    });
    
    if let Err(e) = result {
        error!("Error: {}", e);
        
        // Display a more helpful error message if we can
        let e_str = e.to_string().to_lowercase();
        if e_str.contains("protocol not available") {
            error!("This tool requires a wlroots-based Wayland compositor (like Sway or Hyprland)");
            error!("with the wlr-screencopy protocol enabled.");
        }
        
        return Err(e);
    }
    
    Ok(())
}
