import React, { useState, useEffect } from 'react';

interface Task {
  title: string;
  instructions: string;
  duration: number; 
}

const tasks: Task[] = [
  { title: 'Task 1', instructions: 'Build a circuit with a lamp that can be turned on and off using a switch', duration: 10 },
  { title: 'Task 2', instructions: 'Build a circuit with a led and motor in series that can be turned on and off using a button', duration: 15 },
  { title: 'Task 3', instructions: 'Build a circuit with a led and lamp where the led is turned on by a switch and the lamp by a button', duration: 15 },
  { title: 'Task 4', instructions: 'Build a circuit with a music box plays music through a speaker when a switch is turned on once then stops', duration: 15 },
];

const TaskTimer: React.FC = () => {
  const [currentTaskIndex, setCurrentTaskIndex] = useState(-1);
  const [timeLeft, setTimeLeft] = useState(0);
  const [allTasksCompleted, setAllTasksCompleted] = useState(false);
  const [showRemoveMessage, setShowRemoveMessage] = useState(false);
  const [piecesRemoved, setPiecesRemoved] = useState(false);
  const [showStartScreen, setShowStartScreen] = useState(true);

  useEffect(() => {
    if (currentTaskIndex !== -1) {
      setTimeLeft(tasks[currentTaskIndex].duration);
      setShowRemoveMessage(false);
      setPiecesRemoved(false);
      setShowStartScreen(false);
    }
  }, [currentTaskIndex]);

  useEffect(() => {
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
      {showStartScreen && (
        <div>
          <h1>Welcome to Collaborative Electronic Circuit Builder</h1>
          <p>This application will guide you through a series of electric circuit building tasks. Each task has a set duration, shown in seconds, and once the time is up, you'll be prompted to remove all pieces from the board before moving on to the next task. Please build all circuits within the board space and keep your hands by your side when not interacting with or pointing to pieces or the board.</p>
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