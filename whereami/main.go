package main

import (
	"encoding/json"
	"fmt"
	"net"
	"net/http"
	"os"
	"strconv"
	"time"
)

type ResponseData struct {
	DestIP      string              `json:"dest_ip"`
	DestPort    int                 `json:"dest_port"`
	HTTPHeaders map[string][]string `json:"http_headers"`
	Namespace   string              `json:"namespace"`
	NodeName    string              `json:"node_name"`
	PodName     string              `json:"pod_name"`
	SourceIP    string              `json:"source_ip"`
	SourcePort  int                 `json:"source_port"`
	Timestamp   string              `json:"timestamp"`
}

func main() {
	http.HandleFunc("/", func(w http.ResponseWriter, r *http.Request) {
		podName := os.Getenv("POD_NAME")
		nodeName := os.Getenv("NODE_NAME")
		podIP := os.Getenv("POD_IP")
		namespace := os.Getenv("NAMESPACE")
		timestamp := time.Now().Format(time.RFC3339)

		sourceIP, sourcePortStr, _ := net.SplitHostPort(r.RemoteAddr)
		sourcePort, _ := strconv.Atoi(sourcePortStr)

		data := ResponseData{
			DestIP:      podIP,
			DestPort:    80,
			HTTPHeaders: r.Header,
			Namespace:   namespace,
			NodeName:    nodeName,
			PodName:     podName,
			SourceIP:    sourceIP,
			SourcePort:  sourcePort,
			Timestamp:   timestamp,
		}

		jsonData, err := json.MarshalIndent(data, "", "  ")
		if err != nil {
			http.Error(w, "Error generating JSON response", http.StatusInternalServerError)
			return
		}

		w.Header().Set("Content-Type", "application/json")
		fmt.Fprint(w, string(jsonData))
	})

	fmt.Println("Starting server on port 80")
	err := http.ListenAndServe(":80", nil)
	if err != nil {
		fmt.Printf("Error starting server: %v\n", err)
		os.Exit(1)
	}
}
