package main

import (
	"bytes"
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	"os/exec"
)

type ExecuteRequest struct {
	Lang    string `json:"lang"`
	Content string `json:"content"`
}

type ExecuteResponse struct {
	Stdout string `json:"stdout"`
	Stderr string `json:"stderr"`
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

	resp := runPython(req.Content)

	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusOK)
	json.NewEncoder(w).Encode(resp)
}

func main() {
	http.HandleFunc("/api/execute", executeHandler)
	log.Println("Server started on :8000")
	log.Fatal(http.ListenAndServe(":8000", nil))
}

func runPython(code string) ExecuteResponse {
	cmd := exec.Command("python3", "-c", code)

	var stdout bytes.Buffer
	var stderr bytes.Buffer
	cmd.Stdout = &stdout
	cmd.Stderr = &stderr

	err := cmd.Run()
	if err != nil && stderr.String() == "" {
		fmt.Printf("Error while running Python: %v", err)
	}

	return ExecuteResponse{
		Stdout: stdout.String(),
		Stderr: stderr.String(),
	}
}
