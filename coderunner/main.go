package main

import (
	"bytes"
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	"os/exec"
	"runtime"
	"sync"
)

type ExecuteRequest struct {
	Lang    string `json:"lang"`
	Content string `json:"content"`
}

type ExecuteResponse struct {
	Stdout string `json:"stdout"`
	Stderr string `json:"stderr"`
}

type Job struct {
	Request ExecuteRequest
}

type Result struct {
	Response ExecuteResponse
}

var (
	jobs    chan Job
	results chan Result
	wg      sync.WaitGroup
)

func worker() {
	defer wg.Done()
	for job := range jobs {
		results <- Result{Response: runPython(job.Request.Content)}
	}
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

	jobs <- Job{Request: req}
	result := <-results

	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusOK)
	err = json.NewEncoder(w).Encode(result.Response)
	if err != nil {
		fmt.Printf("Error while encoding response: %v", err)
		http.Error(w, "Internal Error", http.StatusInternalServerError)
		return
	}
}

func main() {
	numCPU := runtime.NumCPU()
	runtime.GOMAXPROCS(numCPU)

	numWorkers := numCPU * 2
	jobs = make(chan Job, numWorkers)
	results = make(chan Result, numWorkers)

	for i := 0; i < numWorkers; i++ {
		wg.Add(1)
		go worker()
	}

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
