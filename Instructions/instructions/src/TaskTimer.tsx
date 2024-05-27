import React, { useState, useEffect } from 'react';

interface Task {
  title: string;
  instructions: string;
  duration: number; // in seconds
}

const tasks: Task[] = [
  { title: 'Task 1', instructions: 'Do something for task 1', duration: 10 },
  { title: 'Task 2', instructions: 'Do something for task 2', duration: 15 },
  // Add more tasks as needed
];

const TaskTimer: React.FC = () => {
  const [currentTaskIndex, setCurrentTaskIndex] = useState(-1); // Initialize to -1 to represent start screen
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