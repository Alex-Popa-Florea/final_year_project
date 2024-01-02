// Note: This file has not been compiled, I just copied it from the official website:
// https://learn.microsoft.com/en-us/azure/ai-services/speech-service/get-started-stt-diarization?tabs=linux&pivots=programming-language-cpp
// One may need to edit the Makefile in order to compile this file

#include <iostream> 
#include <stdlib.h>
#include <speechapi_cxx.h>
#include <future>

using namespace Microsoft::CognitiveServices::Speech;
using namespace Microsoft::CognitiveServices::Speech::Audio;
using namespace Microsoft::CognitiveServices::Speech::Transcription;

std::string GetEnvironmentVariable(const char* name);

int main()
{
    // This example requires environment variables named "SPEECH_KEY" and "SPEECH_REGION"
    auto speechKey = GetEnvironmentVariable("SPEECH_KEY");
    auto speechRegion = GetEnvironmentVariable("SPEECH_REGION");

    if ((size(speechKey) == 0) || (size(speechRegion) == 0)) {
        std::cout << "Please set both SPEECH_KEY and SPEECH_REGION environment variables." << std::endl;
        return -1;
    }

    auto speechConfig = SpeechConfig::FromSubscription(speechKey, speechRegion);

    speechConfig->SetSpeechRecognitionLanguage("en-US");

    auto audioConfig = AudioConfig::FromWavFileInput("katiesteve.wav");
    auto conversationTranscriber = ConversationTranscriber::FromConfig(speechConfig, audioConfig);

    // promise for synchronization of recognition end.
    std::promise<void> recognitionEnd;

    // Subscribes to events.
    conversationTranscriber->Transcribing.Connect([](const SpeechRecognitionEventArgs& e)
        {
            std::cout << "TRANSCRIBING:" << e.Result->Text << std::endl;
        });

    conversationTranscriber->Transcribed.Connect([](const SpeechRecognitionEventArgs& e)
        {
            if (e.Result->Reason == ResultReason::RecognizedSpeech)
            {
                std::cout << "TRANSCRIBED: Text=" << e.Result->Text << std::endl;
                std::cout << "Speaker ID=" << e.Result->SpeakerId << std::endl;
            }
            else if (e.Result->Reason == ResultReason::NoMatch)
            {
                std::cout << "NOMATCH: Speech could not be transcribed." << std::endl;
            }
        });

    conversationTranscriber->Canceled.Connect([&recognitionEnd](const SpeechRecognitionCanceledEventArgs& e)
        {
            auto cancellation = CancellationDetails::FromResult(e.Result);
            std::cout << "CANCELED: Reason=" << (int)cancellation->Reason << std::endl;

            if (cancellation->Reason == CancellationReason::Error)
            {
                std::cout << "CANCELED: ErrorCode=" << (int)cancellation->ErrorCode << std::endl;
                std::cout << "CANCELED: ErrorDetails=" << cancellation->ErrorDetails << std::endl;
                std::cout << "CANCELED: Did you set the speech resource key and region values?" << std::endl;
            }
            else if (cancellation->Reason == CancellationReason::EndOfStream)
            {
                std::cout << "CANCELED: Reach the end of the file." << std::endl;
            }
        });

    conversationTranscriber->SessionStopped.Connect([&recognitionEnd](const SessionEventArgs& e)
        {
            std::cout << "Session stopped.";
            recognitionEnd.set_value(); // Notify to stop recognition.
        });

    conversationTranscriber->StartTranscribingAsync().wait();

    // Waits for recognition end.
    recognitionEnd.get_future().wait();

    conversationTranscriber->StopTranscribingAsync().wait();
}

std::string GetEnvironmentVariable(const char* name)
{
#if defined(_MSC_VER)
    size_t requiredSize = 0;
    (void)getenv_s(&requiredSize, nullptr, 0, name);
    if (requiredSize == 0)
    {
        return "";
    }
    auto buffer = std::make_unique<char[]>(requiredSize);
    (void)getenv_s(&requiredSize, buffer.get(), requiredSize, name);
    return buffer.get();
#else
    auto value = getenv(name);
    return value ? value : "";
#endif
}