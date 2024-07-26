package main

import (
	"encoding/json"
	"fmt"
	"log"
	"net/http"
)

type ExecuteRequest struct {
	Lang    string `json:"lang"`
	Content string `json:"content"`
}

func executeHandler(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		http.Error(w, "Invalid request method", http.StatusMethodNotAllowed)
		return
	}

	var req ExecuteRequest
	decoder := json.NewDecoder(r.Body)
	err := decoder.Decode(&req)
	if err != nil {
		http.Error(w, "Bad request", http.StatusBadRequest)
		return
	}

	response := fmt.Sprintf("Received lang: %s, content: %s", req.Lang, req.Content)
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusOK)
	json.NewEncoder(w).Encode(map[string]string{"message": response})
}

func main() {
	http.HandleFunc("/api/execute", executeHandler)
	log.Println("Server started on :8000")
	log.Fatal(http.ListenAndServe(":8000", nil))
}
