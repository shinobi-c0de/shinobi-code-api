use bytes::Bytes;
use pyo3::prelude::*;
use pyo3::types::{PyBytes, PyModule};
use rust_translate::translate;

pub async fn gtranslate(text: String) -> String {
    let translated_text = translate(text.as_str(), "ja", "en").await.unwrap();
    translated_text
}

pub fn google_search(query: String) -> Result<String, String> {
    Python::with_gil(|py| {
        // Import the Python module
        let sys = py.import("sys").map_err(|e| e.to_string())?;
        let path = sys.getattr("path").map_err(|e| e.to_string())?;
        path.call_method1("append", ("./",)) // Add current directory to Python path
            .map_err(|e| e.to_string())?;

        let module = PyModule::import(py, "gsearch").map_err(|e| e.to_string())?;
        let func = module.getattr("Gsearch").map_err(|e| e.to_string())?;

        let result = func.call1((query,)).map_err(|e| e.to_string())?;
        let text: String = result.extract().map_err(|e| e.to_string())?;
        Ok(text)
    })
}

pub fn transcribe_audio(audio_data: &Bytes, api_key: String) -> Result<String, String> {
    Python::with_gil(|py| {
        // Import the Python module
        let sys = py.import("sys").map_err(|e| e.to_string())?;
        let path = sys.getattr("path").map_err(|e| e.to_string())?;
        path.call_method1("append", ("./",)) // Add current directory to Python path
            .map_err(|e| e.to_string())?;

        let module = PyModule::import(py, "speech").map_err(|e| e.to_string())?;
        let py_audio_data = PyBytes::new(py, &audio_data);
        let func = module
            .getattr("recognize_speech")
            .map_err(|e| e.to_string())?;

        let result = func
            .call1((py_audio_data, api_key))
            .map_err(|e| e.to_string())?;
        let text: String = result.extract().map_err(|e| e.to_string())?;
        Ok(text)
    })
}
