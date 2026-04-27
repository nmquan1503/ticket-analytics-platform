import React, { useState, useRef, useEffect } from 'react';
import { MessageSquare, X, Send, Sparkles, Terminal, Database } from 'lucide-react';

export default function AICopilot() {
  const [isOpen, setIsOpen] = useState(false);
  const [inputVal, setInputVal] = useState('');
  const [messages, setMessages] = useState([
    { 
      id: 1, 
      role: 'bot', 
      type: 'text', 
      content: 'Xin chào! Tôi là AI Copilot (Trợ lý Dữ liệu). Bạn có thể hỏi tôi về báo cáo vận hành hoặc gõ trực tiếp lệnh SQL (bắt đầu bằng SELECT) để trích xuất dữ liệu gốc.' 
    }
  ]);
  const messagesEndRef = useRef(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isOpen]);

  const handleSend = () => {
    if (!inputVal.trim()) return;
    
    const userMsg = inputVal.trim();
    // Thêm tin nhắn của User
    const newMessages = [...messages, { id: Date.now(), role: 'user', type: 'text', content: userMsg }];
    setMessages(newMessages);
    setInputVal('');

    // Giả lập Backend xử lý (Delay 1s)
    setTimeout(() => {
      const isSQL = userMsg.toUpperCase().startsWith('SELECT') || userMsg.toUpperCase().includes('FROM');
      
      if (isSQL) {
        setMessages(prev => [...prev, {
          id: Date.now() + 1,
          role: 'bot',
          type: 'sql-result',
          query: userMsg,
          content: 'Query executed successfully. Result parsed from scc_ht_schema dimensions.'
        }]);
      } else {
        const botReplies = [
          "Dựa trên dữ liệu hiện tại, tỷ lệ đúng hạn (SLA) đang có dấu hiệu giảm nhẹ ở khu vực miền Bắc.",
          "Hệ thống Core IP đang là nhóm thiết bị gây ra nhiều sự cố gián đoạn nhất trong 7 ngày qua.",
          "Bạn có thể dùng thẻ lọc phía trên để bóc tách dữ liệu theo mức ưu tiên Mức 5 (Khẩn cấp)."
        ];
        const reply = botReplies[Math.floor(Math.random() * botReplies.length)];
        
        setMessages(prev => [...prev, {
          id: Date.now() + 1,
          role: 'bot',
          type: 'text',
          content: reply
        }]);
      }
    }, 1000);
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <>
      {/* Floating Action Button */}
      <div className="fixed bottom-6 right-6 z-50">
        <button 
          onClick={() => setIsOpen(true)}
          className={`relative flex items-center justify-center p-4 rounded-full bg-gradient-to-r from-indigo-600 to-blue-500 text-white shadow-lg hover:shadow-xl hover:scale-105 transition-all duration-300 ${isOpen ? 'scale-0 opacity-0' : 'scale-100 opacity-100'}`}
        >
          <Sparkles className="w-6 h-6 animate-pulse" />
          {/* Notification Ping */}
          <span className="absolute top-0 right-0 flex h-3 w-3">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-white opacity-75"></span>
            <span className="relative inline-flex rounded-full h-3 w-3 bg-red-500 border border-white"></span>
          </span>
        </button>
      </div>

      {/* Backdrop (Optional: if we want to dim the background. We'll skip dimming to let user look at charts while chatting) */}

      {/* Sidebar Drawer */}
      <div className={`fixed top-0 right-0 h-full w-[400px] bg-white shadow-2xl z-50 transform transition-transform duration-300 ease-in-out flex flex-col ${isOpen ? 'translate-x-0' : 'translate-x-full'} border-l border-gray-100`}>
        
        {/* Header */}
        <div className="flex items-center justify-between px-5 py-4 bg-indigo-900 border-b border-indigo-800 text-white">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-indigo-800 rounded-lg">
              <Database className="w-4 h-4 text-indigo-200" />
            </div>
            <div>
              <h2 className="text-sm font-bold tracking-wide flex items-center gap-2">
                SQL WORKBENCH & AI
                <span className="px-2 py-0.5 rounded text-[10px] bg-green-500/20 text-green-300 border border-green-500/30">ONLINE</span>
              </h2>
              <p className="text-xs text-indigo-300">Data Analytics Copilot</p>
            </div>
          </div>
          <button 
            onClick={() => setIsOpen(false)}
            className="p-2 text-indigo-300 hover:text-white hover:bg-indigo-800 rounded-lg transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Chat Content */}
        <div className="flex-1 overflow-y-auto p-4 space-y-6 bg-slate-50">
          {messages.map((msg) => (
            <div key={msg.id} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
              
              {/* Bot Avatar */}
              {msg.role === 'bot' && (
                <div className="flex-shrink-0 w-8 h-8 rounded-full bg-indigo-100 flex items-center justify-center border border-indigo-200 mr-3 mt-1">
                  <Sparkles className="w-4 h-4 text-indigo-600" />
                </div>
              )}

              <div className={`max-w-[85%] ${msg.role === 'user' ? 'order-1' : 'order-2'}`}>
                {msg.role === 'user' && (
                  <div className="bg-indigo-600 text-white px-4 py-2.5 rounded-2xl rounded-tr-sm shadow-sm text-sm whitespace-pre-wrap font-medium">
                    {msg.content}
                  </div>
                )}

                {msg.role === 'bot' && msg.type === 'text' && (
                  <div className="bg-white border border-gray-100 text-gray-700 px-4 py-3 rounded-2xl rounded-tl-sm shadow-sm text-sm leading-relaxed">
                    {msg.content}
                  </div>
                )}

                {msg.role === 'bot' && msg.type === 'sql-result' && (
                  <div className="bg-white border border-gray-200 rounded-xl overflow-hidden shadow-sm">
                    {/* SQL Panel Header */}
                    <div className="bg-gray-100 px-3 py-2 border-b border-gray-200 flex items-center gap-2">
                      <Terminal className="w-4 h-4 text-gray-500" />
                      <span className="text-xs font-mono font-semibold text-gray-600 truncate">{msg.query}</span>
                    </div>
                    {/* SQL Panel Table */}
                    <div className="overflow-x-auto">
                      <table className="w-full text-left border-collapse">
                        <thead>
                          <tr className="bg-gray-50 text-[10px] text-gray-400 uppercase tracking-wider">
                            <th className="px-3 py-2 border-b border-gray-200 font-semibold">TICKET_ID</th>
                            <th className="px-3 py-2 border-b border-gray-200 font-semibold">STATUS</th>
                            <th className="px-3 py-2 border-b border-gray-200 font-semibold">ACT_TIME</th>
                          </tr>
                        </thead>
                        <tbody className="text-xs text-gray-700 font-medium">
                          <tr className="hover:bg-gray-50 border-b border-gray-100">
                            <td className="px-3 py-2">SC251025001</td>
                            <td className="px-3 py-2 text-emerald-600">Resolved</td>
                            <td className="px-3 py-2 font-mono text-gray-500">65m</td>
                          </tr>
                          <tr className="hover:bg-gray-50 border-b border-gray-100">
                            <td className="px-3 py-2">SC251025002</td>
                            <td className="px-3 py-2 text-amber-600">Inprogress</td>
                            <td className="px-3 py-2 font-mono text-gray-500">12m</td>
                          </tr>
                          <tr className="hover:bg-gray-50">
                            <td className="px-3 py-2">SC251025003</td>
                            <td className="px-3 py-2 text-rose-600">New</td>
                            <td className="px-3 py-2 font-mono text-gray-500">0m</td>
                          </tr>
                        </tbody>
                      </table>
                    </div>
                    <div className="bg-emerald-50 px-3 py-1.5 border-t border-emerald-100 text-[10px] font-medium text-emerald-600">
                      Hiển thị 3 / 1248 rows (0.012s)
                    </div>
                  </div>
                )}
              </div>
            </div>
          ))}
          <div ref={messagesEndRef} />
        </div>

        {/* Input Area */}
        <div className="p-4 bg-white border-t border-gray-100">
          <div className="relative flex items-end bg-gray-50 border border-gray-200 rounded-xl focus-within:ring-2 focus-within:ring-indigo-100 focus-within:border-indigo-400 transition-all shadow-inner">
            <textarea
              value={inputVal}
              onChange={(e) => setInputVal(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Gõ lệnh SQL hoặc đặt câu hỏi..."
              className="w-full bg-transparent border-none focus:ring-0 resize-none text-sm p-3 min-h-[44px] max-h-[120px] outline-none text-gray-800 placeholder-gray-400"
              rows={1}
            />
            <button 
              onClick={handleSend}
              disabled={!inputVal.trim()}
              className="p-2 m-1.5 text-white bg-indigo-600 rounded-lg hover:bg-indigo-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex-shrink-0"
            >
              <Send className="w-4 h-4" />
            </button>
          </div>
          <div className="mt-2 text-center">
            <span className="text-[10px] text-gray-400">Shift + Enter để xuống dòng</span>
          </div>
        </div>
      </div>
    </>
  );
}
