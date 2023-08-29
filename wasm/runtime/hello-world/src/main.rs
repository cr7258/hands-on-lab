use std::thread;
use std::time::Duration;

fn main() {
    loop {
        println!("Hello, World!");
        thread::sleep(Duration::from_secs(1));
    }
}