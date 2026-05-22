import React, { useEffect, useState } from 'react';

function App() {
  const [socket, setSocket] = useState(null);
  const [log, setLog] = useState([]);
  const [myHand, setMyHand] = useState([]);
  const [centerCard, setCenterCard] = useState(null);
  const [myRole, setMyRole] = useState('');
  const [currentTurn, setCurrentTurn] = useState('');
  const [winner, setWinner] = useState(null);

  useEffect(() => {
    const WS_URL = process.env.REACT_APP_WS_URL || 'ws://localhost:8000/ws/game/lobby1/';
    const newSocket = new WebSocket(WS_URL);

    newSocket.onmessage = (event) => {
      const data = JSON.parse(event.data);
      
      if (data.type === 'system_msg') {
        setMyRole(data.role);
        setLog((prev) => [...prev, data.message]);
      } else if (data.type === 'game_start_broadcast') {
        setCenterCard(data.top_card);
        setCurrentTurn(data.turn);
        setWinner(null);
        setLog((prev) => [...prev, data.message]);
        if (data.hand) setMyHand(data.hand);
      } else if (data.type === 'update_center') {
        setCenterCard(data.card);
        setCurrentTurn(data.turn);
        setLog((prev) => [...prev, data.message]);
      } else if (data.type === 'remove_card') {
        setMyHand((prevHand) => {
          const index = prevHand.findIndex(c => c.planet === data.card.planet && c.cargo === data.card.cargo);
          if (index !== -1) {
            const newHand = [...prevHand];
            newHand.splice(index, 1);
            return newHand;
          }
          return prevHand;
        });
      } else if (data.type === 'card_drawn') {
        setMyHand((prevHand) => [...prevHand, data.card]);
        setLog((prev) => [...prev, data.message]);
      } else if (data.type === 'card_drawn_multiple') {
        setMyHand((prevHand) => [...prevHand, ...data.cards]);
        setLog((prev) => [...prev, data.message]);
      } else if (data.type === 'turn_switch') {
        setCurrentTurn(data.turn);
        setLog((prev) => [...prev, data.message]);
      } else if (data.type === 'game_over') {
        setWinner(data.winner);
        setLog((prev) => [...prev, data.message]);
        setMyHand([]); 
      } else if (data.type === 'error') {
        setLog((prev) => [...prev, data.message]);
      }
    };

    setSocket(newSocket);
    return () => newSocket.close();
  }, []);

  const startGame = () => { if (socket) socket.send(JSON.stringify({ action: 'start_game' })); };

  const playCard = (card) => {
    if (currentTurn !== myRole) return;
    if (socket) socket.send(JSON.stringify({ action: 'play_card', card: card }));
  };

  const drawCard = () => {
    if (currentTurn !== myRole) return;
    if (socket) socket.send(JSON.stringify({ action: 'draw_card' }));
  };

  const isMyTurn = currentTurn === myRole;

  // --- UI RENDERING ---
  
  if (winner) {
    const iWon = winner === myRole;
    return (
      <div className="min-h-screen bg-slate-950 flex flex-col items-center justify-center font-mono text-slate-200">
        <h1 className={`text-6xl font-black uppercase tracking-widest drop-shadow-lg ${iWon ? 'text-green-400 shadow-green-400' : 'text-red-500 shadow-red-500'}`}>
          {iWon ? 'Victory' : 'Defeat'}
        </h1>
        <p className="mt-6 text-xl text-slate-400">
          {iWon ? 'You successfully emptied your cargo hold.' : 'Your opponent beat you to the drop.'}
        </p>
        {myRole === 'player_1' && (
           <button 
             onClick={startGame} 
             className="mt-12 px-8 py-4 bg-blue-600 hover:bg-blue-500 text-white font-bold rounded shadow-[0_0_15px_rgba(37,99,235,0.5)] transition-all uppercase tracking-wider"
           >
             Initialize New Launch
           </button>
        )}
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-950 text-slate-200 p-8 font-mono">
      
      {/* Header */}
      <div className="flex justify-between items-end mb-8 border-b border-slate-800 pb-4">
        <div>
          <h1 className="text-3xl font-black text-blue-400 tracking-widest uppercase drop-shadow-md">Galactic Cargo</h1>
          <p className="text-xs text-slate-500 mt-1 uppercase tracking-widest">Command Terminal v1.0</p>
        </div>
        <div className="text-right">
          <span className="text-sm text-slate-500 uppercase tracking-widest">Operator ID</span>
          <div className="text-xl font-bold text-slate-300">{myRole.replace('_', ' ').toUpperCase()}</div>
        </div>
      </div>
      
      {/* Start Button */}
      {myRole === 'player_1' && !centerCard && (
        <button 
          onClick={startGame} 
          className="mb-8 px-6 py-3 bg-blue-600 hover:bg-blue-500 text-white font-bold rounded shadow-[0_0_10px_rgba(37,99,235,0.3)] transition-all uppercase tracking-wide"
        >
          Initialize Launch Sequence
        </button>
      )}

      {/* Turn Banner */}
      {currentTurn && (
        <div className={`py-3 px-6 text-center font-black tracking-widest rounded-md mb-8 uppercase shadow-lg transition-colors ${isMyTurn ? 'bg-green-500 text-slate-950 shadow-green-500/20' : 'bg-red-500 text-slate-950 shadow-red-500/20'}`}>
          {isMyTurn ? "Your Turn: Clear to Dock" : "Opponent's Turn: Stand By"}
        </div>
      )}

      {/* Opponent's Hand */}
      {centerCard && (
         <div className="mb-8 opacity-40 pointer-events-none">
           <h3 className="text-xs text-slate-500 uppercase tracking-widest mb-2">Opponent's Hold</h3>
           <div className="flex gap-2">
             {[1, 2, 3, 4, 5].map((_, i) => (
               <div key={i} className="w-10 h-16 border border-slate-700 rounded bg-slate-900"></div>
             ))}
           </div>
         </div>
      )}

      {/* Terminal Log */}
      <div className="bg-black/50 p-4 border border-blue-500/30 rounded-lg mb-12 h-40 overflow-y-auto font-mono text-sm shadow-inner">
        {log.slice(-6).map((msg, i) => (
          <p key={i} className={`m-0 mb-1 ${msg.includes('⚠️') ? 'text-red-400' : (msg.includes('🏆') ? 'text-yellow-400' : 'text-green-400')}`}>
            <span className="opacity-50 mr-2">{'>'}</span> {msg}
          </p>
        ))}
      </div>

      {/* Center Board */}
      {centerCard && (
        <div className="mb-16">
          <h2 className="text-center text-sm text-slate-500 uppercase tracking-widest mb-6">Current Target Destination</h2>
          <div className="flex justify-center gap-8 items-center">
              
              {/* Target Card */}
              <div className="border-2 border-yellow-500 bg-slate-900 p-6 rounded-xl w-40 h-56 flex flex-col justify-center items-center text-center shadow-[0_0_20px_rgba(234,179,8,0.15)] transform scale-110">
                <strong className="text-yellow-400 text-lg mb-4 uppercase tracking-wider">{centerCard.planet}</strong>
                <span className="text-slate-200">{centerCard.cargo}</span>
              </div>
              
              {/* Draw Pile */}
              <div 
                onClick={drawCard}
                className={`border-2 border-dashed border-slate-700 bg-slate-900/50 p-6 rounded-xl w-40 h-56 flex items-center justify-center text-center transition-all ${isMyTurn ? 'cursor-pointer hover:border-slate-500 hover:bg-slate-800' : 'opacity-50 cursor-not-allowed'}`}
              >
                <strong className="text-slate-500 tracking-widest uppercase">Draw<br/>Cargo</strong>
              </div>

          </div>
        </div>
      )}

      {/* Player Hand */}
      {centerCard && (
        <div>
          <h2 className="text-sm text-slate-500 uppercase tracking-widest mb-4">Your Cargo Hold</h2>
          <div className="flex flex-wrap gap-4">
            {myHand.map((card, index) => (
              <div 
                key={index} 
                onClick={() => playCard(card)} 
                className={`border-2 p-4 rounded-xl bg-slate-800 text-center w-36 h-48 flex flex-col justify-center transition-all duration-200 ${isMyTurn ? 'border-slate-600 hover:border-blue-400 hover:-translate-y-2 hover:shadow-[0_10px_20px_rgba(37,99,235,0.2)] cursor-pointer' : 'border-slate-800 opacity-50 cursor-not-allowed'}`}
              >
                <strong className="text-blue-300 mb-4 tracking-wider uppercase text-sm">{card.planet}</strong>
                <span className="text-slate-300">{card.cargo}</span>
              </div>
            ))}
          </div>
        </div>
      )}

    </div>
  );
}

export default App;