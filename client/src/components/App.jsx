import { useRef, useState } from "react";
import logo from "/audio_lines_icon.svg";
import SessionControls from "./SessionControls";
import Visualizer from "./Visualizer";

const apiDomain = import.meta.env.VITE_API_DOMAIN;
const socketUrl = apiDomain ? `wss://${apiDomain}` : `ws:///localhost:55555`;
const apiUrl = apiDomain ? `https://${apiDomain}` : `http:///localhost:55555`;

export default function App() {
  const [isSessionActive, setIsSessionActive] = useState(false);
  const [isActivating, setIsActivating] = useState(false);
  const [dataChannel, setDataChannel] = useState(null);
  const [micStream, setMicStream] = useState(null);
  const [events, setEvents] = useState([]);
  const [outputStream, setOutputStream] = useState(null);
  const peerConnection = useRef(null);
  const audioElement = useRef(null);
  const websocket = useRef(null); // For Python communication

  async function startSession() {
    try {
      // Create a peer connection for audio
      const pc = new RTCPeerConnection();
      peerConnection.current = pc;

      // Set up audio playback
      audioElement.current = document.createElement("audio");
      audioElement.current.autoplay = true;
      pc.ontrack = (e) => {
        audioElement.current.srcObject = e.streams[0];
        setOutputStream(e.streams[0]);
      };

      // Add local audio track (microphone)
      const ms = await navigator.mediaDevices.getUserMedia({ audio: true });
      setMicStream(ms);
      pc.addTrack(ms.getTracks()[0]);

      // Set up data channel for OpenAI events
      const dc = pc.createDataChannel("oai-events");
      setDataChannel(dc);

      // Start WebSocket for Python server
      const ws = new WebSocket(socketUrl);
      websocket.current = ws;

      ws.onopen = () => {
        console.log("Connected to Python WebSocket server");
      };

      ws.onmessage = (event) => {
        const message = JSON.parse(event.data);
        console.log("Received from Python:", message);
        // Forward Python response to RTCDataChannel
        if (dc && dc.readyState === "open") {
          dc.send(JSON.stringify(message));
        } else {
          console.error("RTCDataChannel not open, cannot forward:", message);
        }
      };

      ws.onclose = () => {
        console.log("Disconnected from Python WebSocket server");
      };

      ws.onerror = (error) => {
        console.error("WebSocket error:", error);
      };

      // WebRTC SDP setup
      const offer = await pc.createOffer();
      await pc.setLocalDescription(offer);

      const sdpResponse = await fetch(`${apiUrl}/openai/sdp`, {
        method: "POST",
        body: JSON.stringify({
          offer_sdp: offer.sdp,
        }),
        headers: {
          "Content-type": "application/json",
        },
      });

      const response = await sdpResponse.json();

      await pc.setRemoteDescription(response.content);

      // Handle data channel events
      dc.onopen = () => {
        console.log("RTCDataChannel opened");
        setIsSessionActive(true);
        setIsActivating(false);
      };

      dc.onmessage = (e) => {
        const event = JSON.parse(e.data);
        // Forward events to Python
        if (ws.readyState === WebSocket.OPEN) {
          ws.send(JSON.stringify(event));
        }
      };

      dc.onclose = () => {
        console.log("RTCDataChannel closed");
        setIsSessionActive(false);
      };
    } catch (error) {
      console.error("Failed to start session:", error);
    }
  }

  function stopSession() {
    if (dataChannel) {
      dataChannel.close();
    }
    if (peerConnection.current) {
      peerConnection.current.getSenders().forEach((sender) => {
        if (sender.track) sender.track.stop();
      });
      peerConnection.current.close();
    }
    if (websocket.current && websocket.current.readyState === WebSocket.OPEN) {
      websocket.current.close();
    }
    if (micStream) {
      micStream.getTracks().forEach((track) => track.stop());
    }
    setIsSessionActive(false);
    setDataChannel(null);
    setMicStream(null);
    setOutputStream(null);
    peerConnection.current = null;
    websocket.current = null;
  }

  function sendClientEvent(message) {
    if (dataChannel && dataChannel.readyState === "open") {
      message.event_id = message.event_id || crypto.randomUUID();
      dataChannel.send(JSON.stringify(message));
    } else {
      console.error("RTCDataChannel not open, cannot send:", message);
    }
  }

  function sendTextMessage(message) {
    const event = {
      type: "conversation.item.create",
      item: {
        type: "message",
        role: "user",
        content: [{ type: "input_text", text: message }],
      },
    };
    sendClientEvent(event);
    sendClientEvent({ type: "response.create" });
  }

  return (
    <>
      <nav className="absolute top-0 left-0 right-0 h-16 flex items-center">
        <div className="flex items-center justify-center gap-4 w-full m-4 pb-2 border-0 border-b border-solid border-gray-200">
          <img style={{ width: "30px" }} src={logo} />

          <h1 className="text-2xl font-bold text-black">
          ESAB Representer
          </h1>
        </div>
      </nav>
      <main className="absolute top-16 left-0 right-0 bottom-0">
        <section className="absolute top-0 left-0 right-0 bottom-0 flex">
          <section className="absolute top-0 left-0 right-0 bottom-32 px-4 overflow-y-auto">
            <Visualizer
              audioInputStream={micStream}
              audioOutputStream={outputStream}
            />
          </section>
          <section className="absolute h-32 left-0 right-0 bottom-0 p-4">
            <SessionControls
              startSession={startSession}
              stopSession={stopSession}
              isActivating={isActivating}
              setIsActivating={setIsActivating}
              sendTextMessage={sendTextMessage}
              isSessionActive={isSessionActive}
              sendClientEvent={sendClientEvent}
              events={events}
            />
          </section>
        </section>
        

      </main>
    </>
  );
}
