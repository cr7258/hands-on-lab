use warp::Filter;

#[tokio::main(flavor = "current_thread")]
async fn main() {
    let hello = warp::get()
        .and(warp::path::end())
        .map(|| "Hello, World!");

    println!("Listening on http://0.0.0.0:8080");
    warp::serve(hello).run(([0, 0, 0, 0], 8080)).await;
}