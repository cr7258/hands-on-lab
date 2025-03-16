import React, { useState, useRef } from "react";
import { TypeAnimation } from "react-type-animation";
import "./App.css";

const ChatInterface = () => {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [currentResponse, setCurrentResponse] = useState("");
  const [apiKey, setApiKey] = useState("");
  const [isStreaming, setIsStreaming] = useState(false);
  const chatContainerRef = useRef(null);

  // Function to scroll to the bottom of the chat container
  const scrollToBottom = () => {
    if (chatContainerRef.current) {
      chatContainerRef.current.scrollTop = chatContainerRef.current.scrollHeight;
    }
  };

  // Call Tongyi Qianwen API with streaming
  const callTongyiQianwenAPI = async (prompt) => {
    if (!apiKey) {
      alert("Please enter your Tongyi Qianwen API key");
      return;
    }

    setIsLoading(true);
    setCurrentResponse("");
    
    // Add the user message to the chat history immediately
    setMessages(prev => [...prev, { role: "user", content: prompt }]);
    
    // Create an assistant message placeholder that will be updated in real-time
    setMessages(prev => [...prev, { role: "assistant", content: "", isStreaming: true }]);

    try {
      // Use the CORS proxy server
      const proxyUrl = "http://localhost:8080/";
      const targetUrl = "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions";
      
      const response = await fetch(proxyUrl + targetUrl, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${apiKey}`,
          "X-Requested-With": "XMLHttpRequest" // Required by cors-anywhere
        },
        body: JSON.stringify({
          model: "qwen-turbo", // Using qwen-turbo as it's more commonly available
          messages: [
            {
              role: "user",
              content: prompt
            }
          ],
          stream: true, // Enable streaming
          temperature: 0.7,
          top_p: 0.8
        })
      });

      if (!response.ok) {
        // Get more details about the error
        const errorText = await response.text();
        console.error('API Error Response:', errorText);
        throw new Error(`API request failed with status ${response.status}: ${errorText}`);
      }
      
      // Log the response headers for debugging
      console.log('Response headers:', [...response.headers.entries()].reduce((obj, [key, value]) => {
        obj[key] = value;
        return obj;
      }, {}));

      const reader = response.body.getReader();
      const decoder = new TextDecoder("utf-8");
      let responseText = "";
      
      // For debugging, log all chunks
      let chunkCounter = 0;
      
      // Create a dedicated logger for SSE messages
      const logSSE = (message, data) => {
        console.log(`%c SSE Message ${chunkCounter} %c ${message}`, 
          'background: #ffeb3b; color: black; font-weight: bold; padding: 2px 5px; border-radius: 3px;', 
          'color: #2196f3;');
        if (data) console.log(data);
      };
      
      while (true) {
        const { done, value } = await reader.read();
        if (done) {
          logSSE('Stream ended');
          break;
        }
        
        const chunk = decoder.decode(value, { stream: true });
        chunkCounter++;
        
        // Log every chunk with a counter
        logSSE(`Chunk ${chunkCounter} received:`, chunk);
        
        try {
          // Handle different response formats
          // 1. Try parsing as SSE (Server-Sent Events) format: data: {...}
          // 2. Try parsing as direct JSON lines
          // 3. Try extracting content from plain text
          
          // Split by lines and process each line
          const lines = chunk.split('\n').filter(line => line.trim());
          
          for (const line of lines) {
            // Special styling for SSE message lines
            const lineNumber = lines.indexOf(line) + 1;
            const logLine = (type, message, data) => {
              console.log(`%c SSE Line ${lineNumber} (${type}) %c ${message}`, 
                'background: #4caf50; color: white; font-weight: bold; padding: 2px 5px; border-radius: 3px;', 
                'color: #ff5722;');
              if (data) console.log(data);
            };
            
            logLine('raw', line);
            
            let jsonData = null;
            
            // Case 1: SSE format - line starts with 'data: '
            if (line.startsWith('data: ')) {
              const jsonStr = line.substring(6).trim();
              
              // Skip '[DONE]' message
              if (jsonStr === '[DONE]') {
                logLine('event', 'Received [DONE] event');
                continue;
              }
              
              try {
                jsonData = JSON.parse(jsonStr);
                logLine('json', 'Successfully parsed SSE data', jsonData);
              } catch (e) {
                logLine('error', 'Not valid JSON in SSE format:', jsonStr);
              }
            } 
            // Case 2: Direct JSON format
            else {
              try {
                jsonData = JSON.parse(line);
                logLine('json', 'Successfully parsed direct JSON', jsonData);
              } catch (e) {
                // Not JSON, might be plain text or other format
                logLine('text', 'Not valid JSON, treating as text');
                
                // Case 3: If it's plain text, just append it
                if (line.trim() && !line.includes('{') && !line.includes('}')) {
                  responseText += line.trim() + ' ';
                  setCurrentResponse(responseText);
                  logLine('append', 'Appended as plain text', responseText);
                  continue;
                }
              }
            }
            
            // Process the JSON data if we have it
            if (jsonData) {
              // Extract content based on Tongyi Qianwen API response format
              let content = '';
              let contentSource = 'unknown';
              
              // Try different possible response structures for OpenAI-compatible API
              if (jsonData.choices?.[0]?.delta?.content) {
                content = jsonData.choices[0].delta.content;
                contentSource = 'choices[0].delta.content';
              } else if (jsonData.choices?.[0]?.message?.content) {
                content = jsonData.choices[0].message.content;
                contentSource = 'choices[0].message.content';
              } else if (jsonData.choices?.[0]?.text) {
                content = jsonData.choices[0].text;
                contentSource = 'choices[0].text';
              } 
              // Fallback to original Tongyi Qianwen API format
              else if (jsonData.output?.choices?.[0]?.message?.content) {
                content = jsonData.output.choices[0].message.content;
                contentSource = 'output.choices[0].message.content';
              } else if (jsonData.output?.choices?.[0]?.delta?.content) {
                content = jsonData.output.choices[0].delta.content;
                contentSource = 'output.choices[0].delta.content';
              } else if (jsonData.output?.choices?.[0]?.content) {
                content = jsonData.output.choices[0].content;
                contentSource = 'output.choices[0].content';
              } else if (jsonData.output?.text) {
                content = jsonData.output.text;
                contentSource = 'output.text';
              } else if (jsonData.text) {
                content = jsonData.text;
                contentSource = 'text';
              }
              
              if (content) {
                logLine('content', `Extracted content from ${contentSource}:`, content);
                responseText += content;
                setCurrentResponse(responseText);
                
                // Update the assistant message in real-time
                setMessages(prev => {
                  const newMessages = [...prev];
                  // Find the last assistant message that is streaming
                  const lastAssistantIndex = newMessages.findIndex(
                    msg => msg.role === 'assistant' && msg.isStreaming
                  );
                  
                  if (lastAssistantIndex !== -1) {
                    // Update the content of the streaming message
                    newMessages[lastAssistantIndex] = {
                      ...newMessages[lastAssistantIndex],
                      content: responseText
                    };
                  }
                  return newMessages;
                });
                
                // Scroll to bottom to show new content
                setTimeout(scrollToBottom, 10);
                
                logLine('update', 'Updated response text', responseText);
              } else {
                logLine('warning', 'No content found in JSON data', jsonData);
              }
            }
          }
        } catch (e) {
          console.error('Error processing chunk:', e, chunk);
          
          // As a fallback, try to use the raw chunk as content
          if (chunk.trim() && !chunk.includes('{') && !chunk.includes('}')) {
            responseText += chunk.trim() + ' ';
            setCurrentResponse(responseText);
          }
        }
      }

      // Finish streaming and mark the message as complete
      setMessages(prev => {
        const newMessages = [...prev];
        // Find the last assistant message that is streaming
        const lastAssistantIndex = newMessages.findIndex(
          msg => msg.role === 'assistant' && msg.isStreaming
        );
        
        if (lastAssistantIndex !== -1) {
          // Mark the message as complete (not streaming anymore)
          newMessages[lastAssistantIndex] = {
            ...newMessages[lastAssistantIndex],
            content: responseText,
            isStreaming: false,
            isComplete: true
          };
        }
        return newMessages;
      });
      
      // Set loading to false since we're done
      setIsLoading(false);
      setTimeout(scrollToBottom, 100);
      
    } catch (error) {
      console.error("Error calling Tongyi Qianwen API:", error);
      setMessages(prev => [...prev, 
        { role: "user", content: prompt },
        { role: "assistant", content: `Error: ${error.message}` }
      ]);
      setIsLoading(false);
      setTimeout(scrollToBottom, 100);
    }
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!input.trim()) return;
    
    callTongyiQianwenAPI(input);
    setInput("");
  };

  return (
    <div className="chat-container">
      <div className="api-key-container">
        <input
          type="password"
          placeholder="Enter your Tongyi Qianwen API key"
          value={apiKey}
          onChange={(e) => setApiKey(e.target.value)}
          className="api-key-input"
        />
      </div>
      
      <div className="chat-messages" ref={chatContainerRef}>
        {messages.map((message, index) => (
          <div key={index} className={`message ${message.role} ${message.isStreaming ? 'streaming' : ''}`}>
            <div className="message-content">
              <div style={{ whiteSpace: "pre-line" }}>{message.content}</div>
              {message.isStreaming && (
                <span className="cursor-blink">|</span>
              )}
            </div>
          </div>
        ))}
        
        {isLoading && messages.length === 0 && (
          <div className="message assistant loading">
            <div className="message-content">
              <div>Loading response...</div>
            </div>
          </div>
        )}
      </div>
      
      <form onSubmit={handleSubmit} className="chat-input-form">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Ask a question..."
          disabled={isLoading}
          className="chat-input"
        />
        <button type="submit" disabled={isLoading} className="send-button">
          {isLoading ? "Sending..." : "Send"}
        </button>
      </form>
    </div>
  );
};

function App() {
  return (
    <div className="app-container">
      <h1>Tongyi Qianwen Chat</h1>
      <ChatInterface />
    </div>
  );
}

export default App;
