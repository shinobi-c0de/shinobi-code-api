mod utils;

use axum::{
    extract::Multipart,
    http::StatusCode,
    response::{IntoResponse, Response},
    routing::{get, post},
    Json, Router,
};
use bytes::Bytes;
use dotenvy::dotenv;
use serde::{Deserialize, Serialize};
use serde_json::json;
use std::{env, net::SocketAddr};
use tower_http::cors::{Any, CorsLayer};
use utils::{google_search, gtranslate, transcribe_audio};

// Request model
#[derive(Deserialize)]
struct TextRequest {
    text: String,
}

// Response model
#[derive(Serialize)]
struct TextResponse {
    text: String,
}

#[tokio::main]
async fn main() {
    dotenv().ok();

    let cors = CorsLayer::new()
        .allow_methods(Any) // Allow all HTTP methods (POST, GET, etc.)
        .allow_headers(Any) // Allow all headers
        .allow_origin(Any); // Allow requests from any origin

    let port: u16 = env::var("PORT")
        .unwrap_or_else(|_| "8080".to_string())
        .parse()
        .expect("PORT must be a valid number");

    let addr = SocketAddr::from(([0, 0, 0, 0], port));
    println!("Listening on http://{}", addr);

    let app = Router::new()
        .route("/", get(hello_world))
        .route("/api/gsearch", post(gsearch))
        .route("/api/translate", post(translate))
        .route("/api/speech2text", post(speech2text))
        .layer(cors); // Apply the CORS middleware

    let listener = tokio::net::TcpListener::bind(&addr).await.unwrap();
    axum::serve(listener, app).await.unwrap();
}

// Handler function
async fn hello_world() -> impl IntoResponse {
    let response = json!({"text": format!("Hello Shinobi, Welcome to Shinobi Code!")});
    (StatusCode::OK, Json(response))
}

async fn gsearch(Json(payload): Json<TextRequest>) -> Result<impl IntoResponse, StatusCode> {
    let query = payload.text;
    //Implement google search
    let text = google_search(query);

    let response = json!({ "text":text });
    Ok((StatusCode::OK, Json(response)))
}

async fn speech2text(mut multipart: Multipart) -> Result<impl IntoResponse, StatusCode> {
    let mut audio_data = Bytes::new(); // Initialize empty Bytes

    while let Some(field) = multipart
        .next_field()
        .await
        .map_err(|_| StatusCode::BAD_REQUEST)?
    {
        //let name = field.name().unwrap_or("unknown");
        //let file_name = field.file_name().unwrap_or("audio.wav").to_string();
        //let content_type = field.content_type().unwrap_or("unknown");

        // Read audio file bytes into a new `Bytes` instance (clearing previous data)
        audio_data = field.bytes().await.map_err(|_| StatusCode::BAD_REQUEST)?;
    }
    // If no audio file was found
    if audio_data.is_empty() {
        let response = json!({"error": "No audio file received"});
        return Ok((StatusCode::BAD_REQUEST, Json(response)));
    }

    // Transcribe Speech To text
    // Get API key safely
    let api_key = env::var("GOOGLE_API_KEY").map_err(|_| StatusCode::INTERNAL_SERVER_ERROR)?;

    // Transcribe Speech To Text (handle potential errors)
    match transcribe_audio(&audio_data, api_key) {
        Ok(transcribed_text) => {
            let response = json!({ "text": transcribed_text });
            Ok((StatusCode::OK, Json(response)))
        }
        Err(err) => {
            let response = json!({ "error": err });
            let status_code = if err.contains("Couldn't understand audio") {
                StatusCode::UNPROCESSABLE_ENTITY // 422 for unintelligible speech
            } else {
                StatusCode::INTERNAL_SERVER_ERROR
            };
            Ok((status_code, Json(response)))
        }
    }
}

async fn translate(Json(payload): Json<TextRequest>) -> impl IntoResponse {
    let text = payload.text;

    let translated_text = gtranslate(text).await;

    // Return the translated text
    let response = TextResponse {
        text: translated_text,
    };

    (StatusCode::OK, Json(response))
    //火遁豪火球の術
}
