import { useEffect } from "react";

const USER_TRANSCRIPTION =
  "conversation.item.input_audio_transcription.completed";

const ASSISTANCE_TRANSCRIPTION = "response.audio_transcript.done";

export default function EventLog({ dataChannel }) {
  const eventsToDisplay = [];

  useEffect(() => {
    if (dataChannel) {
      dataChannel.addEventListener("message", (e) => {
        const event = JSON.parse(e.data);

        if (event.type === USER_TRANSCRIPTION) {
          eventsToDisplay.push(
            <Event role="user" transcript={event?.transcript || ""} />,
          );
        } else if (event.type === ASSISTANCE_TRANSCRIPTION) {
          eventsToDisplay.push(
            <Event role="assistant" transcript={event?.transcript || ""} />,
          );
        }
      });
    }
  }, [dataChannel]);

  return (
    <div className="flex flex-col gap-2 w-full">
      {eventsToDisplay.length === 0 ? (
        <div className="text-gray-500">Awaiting events...</div>
      ) : (
        eventsToDisplay
      )}
    </div>
  );
}

const Event = ({ transcript, role }) => {
  if (!transcript) {
    return null;
  }

  return (
    <div
      className={`flex flex-col gap-2 p-2 rounded-md max-w-[80%] ${
        role === "user"
          ? "ml-auto bg-blue-200 text-gray-900"
          : "mr-auto bg-white text-gray-900"
      }`}
    >
      <div className="text-md font-semibold px-2">{transcript || ""}</div>
    </div>
  );
};
