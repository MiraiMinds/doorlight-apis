import { useEffect, useRef } from "react";
import { motion } from "framer-motion";

const Visualizer = ({ audioInputStream, audioOutputStream }) => {
  const canvasRef = useRef(null);
  const audioContextRef = useRef(null);
  const analyserRef = useRef(null);
  const animationFrameRef = useRef(null);
  const dataArrayRef = useRef(null);

  const CANVAS_SIZE = 600;
  const RADIUS = 200;
  const BAR_WIDTH = 10;
  const BAR_COUNT = 96;
  const FFT_SIZE = 1024;

  useEffect(() => {
    if (audioInputStream || audioOutputStream) {
      startVisualization();
    }

    return () => stopVisualization();
  }, [audioInputStream, audioOutputStream]);

  const startVisualization = () => {
    // Initialize audio context
    const audioContext = new (window.AudioContext ||
      window.webkitAudioContext)();
    audioContextRef.current = audioContext;

    // Create and configure analyser
    const analyser = audioContext.createAnalyser();
    analyserRef.current = analyser;
    analyser.fftSize = FFT_SIZE;
    const bufferLength = analyser.frequencyBinCount;
    dataArrayRef.current = new Uint8Array(bufferLength);

    // Connect audio streams
    if (audioInputStream) {
      const inputSource =
        audioContext.createMediaStreamSource(audioInputStream);
      inputSource.connect(analyser);
    }

    if (audioOutputStream) {
      // For output stream, we might need to handle it differently based on your OpenAI implementation
      const outputSource =
        audioContext.createMediaStreamSource(audioOutputStream);
      outputSource.connect(analyser);
    }

    // Initialize canvas
    const canvas = canvasRef.current;
    canvas.width = CANVAS_SIZE;
    canvas.height = CANVAS_SIZE;

    drawVisualization();
  };

  const drawVisualization = () => {
    const canvas = canvasRef.current;
    const ctx = canvas.getContext("2d");
    const analyser = analyserRef.current;
    const dataArray = dataArrayRef.current;

    if (!canvas || !ctx || !analyser || !dataArray) return;

    ctx.clearRect(0, 0, canvas.width, canvas.height);
    ctx.fillStyle = "transparent";
    ctx.fillRect(0, 0, canvas.width, canvas.height);

    analyser.getByteFrequencyData(dataArray);

    const centerX = canvas.width / 2;
    const centerY = canvas.height / 2;

    ctx.save();
    ctx.translate(centerX, centerY);

    const generatePastelColor = (index) => {
      const hue = index * (360 / BAR_COUNT);
      return `hsl(${hue}, 70%, 80%)`;
    };

    for (let i = 0; i < BAR_COUNT; i++) {
      const value = dataArray[i * 2];
      const barHeight = Math.max(5, (value / 255) * 150);
      const angle = ((i * 360) / BAR_COUNT) * (Math.PI / 180);
      const color = "#010000";

      ctx.save();
      ctx.rotate(angle);

      ctx.beginPath();
      ctx.fillStyle = color;
      ctx.rect(-BAR_WIDTH / 2, -RADIUS, BAR_WIDTH, -barHeight);
      ctx.fill();

      ctx.restore();
    }

    ctx.restore();
    animationFrameRef.current = requestAnimationFrame(drawVisualization);
  };

  const stopVisualization = () => {
    if (animationFrameRef.current) {
      cancelAnimationFrame(animationFrameRef.current);
    }

    if (audioContextRef.current) {
      audioContextRef.current.close();
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 0.5 }}
      className="flex flex-col items-center justify-center"
    >
      <canvas ref={canvasRef} className="border-none" />
    </motion.div>
  );
};

export default Visualizer;
