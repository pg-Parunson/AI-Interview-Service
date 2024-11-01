"""React 컴포넌트 정의"""

EVALUATION_COMPONENT = """
// SVG Icons
const Check = ({ className = "h-4 w-4" }) => (
  <svg xmlns="http://www.w3.org/2000/svg" className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
    <polyline points="20 6 9 17 4 12" />
  </svg>
);

const AlertCircle = ({ className = "h-4 w-4" }) => (
  <svg xmlns="http://www.w3.org/2000/svg" className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
    <circle cx="12" cy="12" r="10" />
    <line x1="12" y1="8" x2="12" y2="12" />
    <line x1="12" y1="16" x2="12.01" y2="16" />
  </svg>
);

// Card Components
const Card = ({ children, className = "" }) => (
  <div className={`rounded-lg border bg-card text-card-foreground shadow-sm ${className}`}>
    {children}
  </div>
);

const CardHeader = ({ children, className = "" }) => (
  <div className={`flex flex-col space-y-1.5 p-6 ${className}`}>
    {children}
  </div>
);

const CardTitle = ({ children, className = "" }) => (
  <h3 className={`text-2xl font-semibold leading-none tracking-tight ${className}`}>
    {children}
  </h3>
);

const CardContent = ({ children, className = "" }) => (
  <div className={`p-6 pt-0 ${className}`}>
    {children}
  </div>
);

const AudioButton = ({ audioData, buttonText = "🔊 듣기" }) => {
  const playAudio = React.useCallback(() => {
    const audio = new Audio(`data:audio/mp3;base64,${audioData}`);
    audio.play().catch(error => console.error('Audio playback error:', error));
  }, [audioData]);

  return (
    <button
      onClick={playAudio}
      className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600 transition-colors inline-flex items-center gap-2"
    >
      <span>🔊</span>
      <span>{buttonText}</span>
    </button>
  );
};

const FeedbackSection = ({ feedback }) => {
  return (
    <div className="max-w-3xl mx-auto space-y-6">
      <Card className="bg-white shadow-md">
        <CardHeader className="bg-blue-50/50 border-b">
          <CardTitle className="text-lg text-blue-800">답변 피드백</CardTitle>
        </CardHeader>
        <CardContent className="pt-6 space-y-4">
          <div className="space-y-4">
            <div>
              <h4 className="font-medium text-gray-700 mb-2">이해도 평가</h4>
              <p className="text-gray-600">{feedback.understanding}</p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="space-y-2">
                <div className="font-medium text-green-700 flex items-center gap-2">
                  <Check className="h-4 w-4" />
                  강점
                </div>
                <ul className="space-y-2">
                  {feedback.strengths.map((strength, idx) => (
                    strength && (
                      <li key={idx} className="text-gray-600 text-sm flex items-start gap-2">
                        <span className="text-green-600 mt-1">•</span>
                        <span>{strength}</span>
                      </li>
                    )
                  ))}
                </ul>
              </div>

              <div className="space-y-2">
                <div className="font-medium text-red-700 flex items-center gap-2">
                  <AlertCircle className="h-4 w-4" />
                  개선 필요
                </div>
                <ul className="space-y-2">
                  {feedback.improvements.map((improvement, idx) => (
                    improvement && (
                      <li key={idx} className="text-gray-600 text-sm flex items-start gap-2">
                        <span className="text-red-600 mt-1">•</span>
                        <span>{improvement}</span>
                      </li>
                    )
                  ))}
                </ul>
              </div>
            </div>

            <div>
              <h4 className="font-medium text-gray-700 mb-2">학습 제안</h4>
              <ul className="space-y-2">
                {feedback.suggestions.map((suggestion, idx) => (
                  suggestion && (
                    <li key={idx} className="text-gray-600 text-sm flex items-start gap-2">
                      <span className="text-blue-600 mt-1">•</span>
                      <span>{suggestion}</span>
                    </li>
                  )
                ))}
              </ul>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

const MessageBubble = ({ role, content, isLast = false }) => {
  const isInterviewer = role === 'interviewer';
  
  return (
    <div className={`flex ${isInterviewer ? 'justify-start' : 'justify-end'} mb-4`}>
      <div className={`
        max-w-[80%] px-4 py-2 rounded-lg
        ${isInterviewer ? 'bg-gray-100 text-gray-800' : 'bg-blue-500 text-white'}
      `}>
        {content}
      </div>
    </div>
  );
};

const ConversationView = ({ messages, feedback }) => {
  return (
    <div className="space-y-4">
      {messages.map((msg, idx) => (
        <MessageBubble 
          key={idx}
          role={msg.role}
          content={msg.content}
          isLast={idx === messages.length - 1}
        />
      ))}
      {feedback && <FeedbackSection feedback={feedback} />}
    </div>
  );
};

export { AudioButton, FeedbackSection, ConversationView };
"""