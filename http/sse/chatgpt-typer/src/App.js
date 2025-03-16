import React, { useState, useRef } from "react";
import "./App.css";

const ChatInterface = () => {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [apiKey, setApiKey] = useState("");
  const chatContainerRef = useRef(null);

  // Function to scroll to the bottom of the chat container
  const scrollToBottom = () => {
    if (chatContainerRef.current) {
      chatContainerRef.current.scrollTop = chatContainerRef.current.scrollHeight;
    }
  };

  // Call API with streaming - this is the core of the typewriter effect
  const callAPI = async (prompt) => {
    if (!apiKey) {
      alert("Please enter your API key");
      return;
    }

    setIsLoading(true);
    
    // Add the user message to the chat history immediately
    setMessages(prev => [...prev, { role: "user", content: prompt }]);
    
    // Create an assistant message placeholder that will be updated in real-time
    // The isStreaming flag is used to show the blinking cursor
    setMessages(prev => [...prev, { role: "assistant", content: "", isStreaming: true }]);

    try {
      // API endpoint setup
      const proxyUrl = "http://localhost:8080/";
      const targetUrl = "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions";
      
      const response = await fetch(proxyUrl + targetUrl, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${apiKey}`,
          "X-Requested-With": "XMLHttpRequest"
        },
        body: JSON.stringify({
          model: "qwen-turbo",
          messages: [{ role: "user", content: prompt }],
          stream: true, // Enable streaming for typewriter effect
          temperature: 0.7
        })
      });

      if (!response.ok) {
        throw new Error(`API request failed with status ${response.status}`);
      }

      // Setup stream reading
      const reader = response.body.getReader();
      const decoder = new TextDecoder("utf-8");
      let responseText = "";
      
      // Process the stream
      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        
        const chunk = decoder.decode(value, { stream: true });
        const lines = chunk.split('\n').filter(line => line.trim());
        
        for (const line of lines) {
          // Handle SSE format (data: {...})  
          if (line.startsWith('data: ')) {
            const jsonStr = line.substring(6).trim();
            if (jsonStr === '[DONE]') continue;
            
            try {
              const jsonData = JSON.parse(jsonStr);
              // Extract content from the response
              const content = jsonData.choices?.[0]?.delta?.content || "";
              if (content) {
                // Add new content to the response text
                responseText += content;
                // Update the message in real-time - this creates the typewriter effect
                updateAssistantMessage(responseText);
              }
            } catch (e) {
              // Skip invalid JSON
            }
          }
        }
      }

      // Finish streaming and mark the message as complete
      setMessages(prev => {
        const newMessages = [...prev];
        const lastAssistantIndex = newMessages.findIndex(
          msg => msg.role === 'assistant' && msg.isStreaming
        );
        
        if (lastAssistantIndex !== -1) {
          // Remove the streaming flag to stop the blinking cursor
          newMessages[lastAssistantIndex] = {
            ...newMessages[lastAssistantIndex],
            content: responseText,
            isStreaming: false
          };
        }
        return newMessages;
      });
      
      setIsLoading(false);
      setTimeout(scrollToBottom, 100);
      
    } catch (error) {
      console.error("Error calling API:", error);
      // Update the streaming message with the error
      setMessages(prev => {
        const newMessages = [...prev];
        const lastAssistantIndex = newMessages.findIndex(
          msg => msg.role === 'assistant' && msg.isStreaming
        );
        
        if (lastAssistantIndex !== -1) {
          newMessages[lastAssistantIndex] = {
            ...newMessages[lastAssistantIndex],
            content: `Error: ${error.message}`,
            isStreaming: false
          };
        }
        return newMessages;
      });
      
      setIsLoading(false);
    }
  };

  // Helper function to update the assistant message in real-time
  // This is the key to creating the typewriter effect
  const updateAssistantMessage = (text) => {
    setMessages(prev => {
      const newMessages = [...prev];
      const lastAssistantIndex = newMessages.findIndex(
        msg => msg.role === 'assistant' && msg.isStreaming
      );
      
      if (lastAssistantIndex !== -1) {
        newMessages[lastAssistantIndex] = {
          ...newMessages[lastAssistantIndex],
          content: text // Update the content incrementally
        };
      }
      return newMessages;
    });
    
    // Scroll to bottom to show new content
    setTimeout(scrollToBottom, 10);
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!input.trim()) return;
    
    callAPI(input);
    setInput("");
  };

  return (
    <div className="chat-container">
      {/* API Key input */}
      <div className="api-key-container">
        <input
          type="password"
          placeholder="Enter your API key"
          value={apiKey}
          onChange={(e) => setApiKey(e.target.value)}
          className="api-key-input"
        />
      </div>
      
      {/* Chat messages - this is where the typewriter effect appears */}
      <div className="chat-messages" ref={chatContainerRef}>
        {messages.map((message, index) => (
          <div key={index} className={`message ${message.role} ${message.isStreaming ? 'streaming' : ''}`}>
            <div className="message-content">
              {/* Display the message content */}
              <div style={{ whiteSpace: "pre-line" }}>{message.content}</div>
              
              {/* Show blinking cursor during streaming - key part of typewriter effect */}
              {message.isStreaming && <span className="cursor-blink">|</span>}
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
      
      {/* Input form */}
      <form onSubmit={handleSubmit} className="chat-input-form">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Type a message..."
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
      <h1>Chat with Typewriter Effect</h1>
      <ChatInterface />
    </div>
  );
}

export default App;
