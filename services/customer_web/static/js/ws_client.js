// SocketIO client — channel A (browser ↔ customer_web)
const socket = io();

socket.on('connect', () => {
  console.log('[WS] connected');
});

socket.on('disconnect', () => {
  console.log('[WS] disconnected');
});

socket.on('status', (data) => {
  console.log('[WS] status:', data);
});
