use warp::Filter;

#[tokio::main(flavor = "current_thread")]
async fn main() {
    let hello = warp::get()
        .and(warp::path::end())
        .map(|| "Hello, World!");

    warp::serve(hello).run(([0, 0, 0, 0], 8080)).await;
}