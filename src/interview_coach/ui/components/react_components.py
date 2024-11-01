"""React 컴포넌트 정의"""

DASHBOARD_COMPONENT = """
// SVG Icons
function Check({ className = "h-4 w-4" }) {
    return React.createElement('svg', {
        xmlns: "http://www.w3.org/2000/svg",
        className: className,
        viewBox: "0 0 24 24",
        fill: "none",
        stroke: "currentColor",
        strokeWidth: "2"
    }, React.createElement('polyline', {
        points: "20 6 9 17 4 12"
    }));
}

function AlertCircle({ className = "h-4 w-4" }) {
    return React.createElement('svg', {
        xmlns: "http://www.w3.org/2000/svg",
        className: className,
        viewBox: "0 0 24 24",
        fill: "none",
        stroke: "currentColor",
        strokeWidth: "2"
    }, [
        React.createElement('circle', {
            cx: "12",
            cy: "12",
            r: "10"
        }),
        React.createElement('line', {
            x1: "12",
            y1: "8",
            x2: "12",
            y2: "12"
        }),
        React.createElement('line', {
            x1: "12",
            y1: "16",
            x2: "12.01",
            y2: "16"
        })
    ]);
}

// Card Components
function Card({ children, className = "" }) {
    return React.createElement('div', {
        className: `rounded-lg border bg-card text-card-foreground shadow-sm ${className}`
    }, children);
}

function CardHeader({ children, className = "" }) {
    return React.createElement('div', {
        className: `flex flex-col space-y-1.5 p-6 ${className}`
    }, children);
}

function CardTitle({ children, className = "" }) {
    return React.createElement('h3', {
        className: `text-2xl font-semibold leading-none tracking-tight ${className}`
    }, children);
}

function CardContent({ children, className = "" }) {
    return React.createElement('div', {
        className: `p-6 pt-0 ${className}`
    }, children);
}

// 통계 컴포넌트
function StatisticCard(props) {
    return React.createElement('div', {
        className: 'bg-white rounded-lg p-6 shadow-md'
    }, [
        React.createElement('h3', {
            className: 'text-lg font-semibold text-gray-700'
        }, props.title),
        React.createElement('p', {
            className: 'text-3xl font-bold text-blue-600 my-2'
        }, props.value),
        React.createElement('p', {
            className: 'text-sm text-gray-500'
        }, props.description)
    ]);
}

function StatisticsDashboard(props) {
    const defaultStats = {
        total_interviews: 0,
        completion_rate: 0,
        position_distribution: {
            "프론트엔드": 0,
            "백엔드": 0,
            "풀스택": 0
        },
        success_rate: 0
    };

    const stats = props.statistics || defaultStats;

    return React.createElement('div', { className: 'space-y-6' }, [

        React.createElement('div', {
            className: 'grid grid-cols-1 md:grid-cols-3 gap-4'
        }, [
            React.createElement(StatisticCard, {
                title: '총 면접 수',
                value: stats.total_interviews.toLocaleString(),
                description: '지금까지 진행된 면접의 총 횟수'
            }),
            React.createElement(StatisticCard, {
                title: '완료율',
                value: `${stats.completion_rate.toLocaleString()}%`,
                description: '전체 면접 중 완료된 면접의 비율'
            }),
            React.createElement(StatisticCard, {
                title: '성공률',
                value: `${stats.success_rate.toLocaleString()}%`,
                description: '완료된 면접 중 합격 기준을 통과한 비율'
            })
        ]),

        React.createElement('div', {
            className: 'bg-white rounded-lg p-6 shadow-md'
        }, [
            React.createElement('h3', {
                className: 'text-lg font-semibold text-gray-700 mb-4'
            }, '포지션별 분포'),
            React.createElement('div', {
                className: 'grid grid-cols-3 gap-4'
            }, Object.entries(stats.position_distribution).map(([position, count]) =>
                React.createElement('div', {
                    key: position,
                    className: 'text-center'
                }, [
                    React.createElement('div', {
                        className: 'font-semibold'
                    }, position),
                    React.createElement('div', {
                        className: 'text-2xl text-blue-600'
                    }, count)
                ])
            ))
        ])
    ]);
}

// 피드백 컴포넌트
function FeedbackSection(props) {
    const feedback = props.feedback;
    
    return React.createElement(Card, { 
        className: 'bg-white shadow-md'
    }, [
        React.createElement(CardHeader, { 
            className: 'bg-blue-50/50 border-b' 
        }, [
            React.createElement(CardTitle, { 
                className: 'text-lg text-blue-800' 
            }, '답변 피드백')
        ]),
        React.createElement(CardContent, { 
            className: 'pt-6 space-y-4'
        }, [
            React.createElement('div', { 
                className: 'space-y-4' 
            }, [
                React.createElement('div', {}, [
                    React.createElement('h4', { 
                        className: 'font-medium text-gray-700 mb-2' 
                    }, '이해도 평가'),
                    React.createElement('p', { 
                        className: 'text-gray-600' 
                    }, feedback.understanding)
                ]),
                React.createElement('div', { 
                    className: 'grid grid-cols-1 md:grid-cols-2 gap-6' 
                }, [
                    // 강점 섹션
                    React.createElement('div', { 
                        className: 'space-y-2' 
                    }, [
                        React.createElement('div', { 
                            className: 'font-medium text-green-700 flex items-center gap-2' 
                        }, [
                            React.createElement(Check, { 
                                className: 'h-4 w-4' 
                            }),
                            '강점'
                        ]),
                        React.createElement('ul', { 
                            className: 'space-y-2' 
                        }, feedback.strengths.map((strength, idx) => 
                            strength && React.createElement('li', {
                                key: idx,
                                className: 'text-gray-600 text-sm flex items-start gap-2'
                            }, [
                                React.createElement('span', { 
                                    className: 'text-green-600 mt-1' 
                                }, '•'),
                                React.createElement('span', {}, strength)
                            ])
                        ))
                    ]),
                    // 개선 필요 섹션
                    React.createElement('div', { 
                        className: 'space-y-2' 
                    }, [
                        React.createElement('div', { 
                            className: 'font-medium text-red-700 flex items-center gap-2' 
                        }, [
                            React.createElement(AlertCircle, { 
                                className: 'h-4 w-4' 
                            }),
                            '개선 필요'
                        ]),
                        React.createElement('ul', { 
                            className: 'space-y-2' 
                        }, feedback.improvements.map((improvement, idx) => 
                            improvement && React.createElement('li', {
                                key: idx,
                                className: 'text-gray-600 text-sm flex items-start gap-2'
                            }, [
                                React.createElement('span', { 
                                    className: 'text-red-600 mt-1' 
                                }, '•'),
                                React.createElement('span', {}, improvement)
                            ])
                        ))
                    ])
                ]),
                // 학습 제안 섹션
                React.createElement('div', {}, [
                    React.createElement('h4', { 
                        className: 'font-medium text-gray-700 mb-2' 
                    }, '학습 제안'),
                    React.createElement('ul', { 
                        className: 'space-y-2' 
                    }, feedback.suggestions.map((suggestion, idx) => 
                        suggestion && React.createElement('li', {
                            key: idx,
                            className: 'text-gray-600 text-sm flex items-start gap-2'
                        }, [
                            React.createElement('span', { 
                                className: 'text-blue-600 mt-1' 
                            }, '•'),
                            React.createElement('span', {}, suggestion)
                        ])
                    ))
                ])
            ])
        ])
    ]);
}

// 메시지 버블 컴포넌트
function MessageBubble(props) {
    const isInterviewer = props.role === 'interviewer';
    
    return React.createElement('div', {
        className: `flex ${isInterviewer ? 'justify-start' : 'justify-end'} mb-4`
    }, [
        React.createElement('div', {
            className: `max-w-[80%] px-4 py-2 rounded-lg ${isInterviewer ? 'bg-gray-100 text-gray-800' : 'bg-blue-500 text-white'}`
        }, props.content)
    ]);
}

// 대화 보기 컴포넌트
function ConversationView(props) {
    return React.createElement('div', {
        className: 'space-y-4'
    }, [
        ...props.messages.map((msg, idx) =>
            React.createElement(MessageBubble, {
                key: idx,
                role: msg.role,
                content: msg.content,
                isLast: idx === props.messages.length - 1
            })
        ),
        props.feedback && React.createElement(FeedbackSection, { 
            feedback: props.feedback 
        })
    ]);
}
"""