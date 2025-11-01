/**
 * Socket.IO client setup
 */
import { io, Socket } from 'socket.io-client';

const SOCKET_URL = process.env.NEXT_PUBLIC_SOCKET_URL || 'http://localhost:5000';

let socket: Socket | null = null;

export const initSocket = (token: string) => {
  if (socket?.connected) {
    return socket;
  }

  socket = io(SOCKET_URL, {
    auth: {
      token
    },
    transports: ['websocket'],
    autoConnect: true
  });

  socket.on('connect', () => {
    console.log('Socket.IO connected');
  });

  socket.on('disconnect', () => {
    console.log('Socket.IO disconnected');
  });

  socket.on('error', (error: any) => {
    console.error('Socket.IO error:', error);
  });

  return socket;
};

export const getSocket = () => {
  return socket;
};

export const disconnectSocket = () => {
  if (socket) {
    socket.disconnect();
    socket = null;
  }
};

// Socket event helpers
export const joinChat = (sessionId: string) => {
  socket?.emit('join_chat', { session_id: sessionId });
};

export const sendMessage = (sessionId: string, content: string) => {
  socket?.emit('send_message', { session_id: sessionId, content });
};

export const sendTyping = (sessionId: string) => {
  socket?.emit('typing', { session_id: sessionId });
};

export const leaveChat = (sessionId: string) => {
  socket?.emit('leave_chat', { session_id: sessionId });
};

export const joinMatchingQueue = () => {
  socket?.emit('join_matching_queue');
};

export const updateStatus = (availability: string) => {
  socket?.emit('status_change', { availability });
};
