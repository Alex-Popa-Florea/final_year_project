import React, { useState, useEffect, useRef } from 'react';

interface Task {
  title: string;
  instructions: string;
  duration: number; 
}

const tasks: Task[] = [
  { title: 'Task 1', instructions: 'Build a circuit with a lamp that can be turned on and off using a switch.', duration: 120 },
  { title: 'Task 2', instructions: 'Build a circuit with a led and motor in series that can be turned on and off using a button.', duration: 135 },
  { title: 'Task 3', instructions: 'Build a circuit with an led that is turned on and off by a switch and the lamp is turned on and off by a button.', duration: 245 },
  { title: 'Task 4', instructions: 'Build a circuit with a music box plays music through a speaker when a switch is turned on once then stops.', duration: 405 },
];

const TaskTimer: React.FC = () => {
  const [currentTaskIndex, setCurrentTaskIndex] = useState(-1);
  const [timeLeft, setTimeLeft] = useState(0);
  const [allTasksCompleted, setAllTasksCompleted] = useState(false);
  const [showRemoveMessage, setShowRemoveMessage] = useState(false);
  const [piecesRemoved, setPiecesRemoved] = useState(false);
  const [showStartScreen, setShowStartScreen] = useState(true);

  const tenSecondAudioRef = useRef<HTMLAudioElement | null>(null);

  useEffect(() => {
    if (currentTaskIndex !== -1) {
      setTimeLeft(tasks[currentTaskIndex].duration);
      setShowRemoveMessage(false);
      setPiecesRemoved(false);
      setShowStartScreen(false);
    }
  }, [currentTaskIndex]);

  useEffect(() => {
    if (timeLeft === 10 && tenSecondAudioRef.current) {
      tenSecondAudioRef.current.play();
    }
    if (timeLeft > 0) {
      const timer = setInterval(() => {
        setTimeLeft(timeLeft - 1);
      }, 1000);
      return () => clearInterval(timer);
    } else {
      setShowRemoveMessage(true);
    }
  }, [timeLeft]);

  const handleBeginTasks = () => {
    setCurrentTaskIndex(0);
  };

  const handleNextTask = () => {
    if (currentTaskIndex < tasks.length - 1) {
      setCurrentTaskIndex(currentTaskIndex + 1);
      setShowRemoveMessage(false);
      setTimeLeft(tasks[currentTaskIndex + 1].duration);
      setPiecesRemoved(false);
    } else {
      setAllTasksCompleted(true);
    }
  };

  const handleConfirmRemovePieces = () => {
    setShowRemoveMessage(false);
    setPiecesRemoved(true);
  };

  if (allTasksCompleted) {
    return (
      <div className="task-container">
        <h1>All tasks done!</h1>
      </div>
    );
  }

  return (
    <div className="task-container">
      <audio ref={tenSecondAudioRef} src="src/assets/sound.mp3" />
      {showStartScreen && (
        <div>
          <h1>Welcome to Collaborative Electronic Circuit Builder</h1>
          <p>This application will guide you through a series of electric circuit building tasks. Each task has a set duration, shown in seconds. At the 10 second remaining mark, a sound will play notifing you of the time. Once the time is up, you'll be prompted to remove all pieces from the board before moving on to the next task. Please build all circuits within the board space and keep your hands by your side when not interacting with or pointing to pieces or the board.</p>
          <button className="next-task-button" onClick={handleBeginTasks}>Begin tasks</button>
        </div>
      )}
      {currentTaskIndex !== -1 && (
        <>
          <h1>{tasks[currentTaskIndex].title}</h1>
          <p>{tasks[currentTaskIndex].instructions}</p>
          {showRemoveMessage && (
            <div>
              <p>Task time finished.</p>
              <p className='remove-message'>Please remove all pieces from the board and then press the button bellow.</p>
              {!piecesRemoved && (
                <button className="next-task-button" onClick={handleConfirmRemovePieces}>Pieces Removed</button>
              )}
            </div>
          )}
          {!showRemoveMessage && !piecesRemoved && (
            <p>Time left: {timeLeft} seconds</p>
          )}
          {!showRemoveMessage && piecesRemoved && (
            <div>
              <p>Task time finished</p>  
              <button className="next-task-button" onClick={handleNextTask}>Next Task</button>
            </div>
          )}
        </>
      )}
    </div>
  );
};

export default TaskTimer;