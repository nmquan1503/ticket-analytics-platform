import React, { useState, useRef, useEffect } from 'react';
import { MessageSquare, X, Send, Sparkles, Terminal, Database, Download, FileText, Loader2 } from 'lucide-react';
import { chatApi } from '../services/api';

export default function AICopilot() {
  const [isOpen, setIsOpen] = useState(false);
  const [inputVal, setInputVal] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [messages, setMessages] = useState([
    { 
      id: 1, 
      role: 'bot', 
      type: 'text', 
      content: 'Xin chào! Tôi là AI Copilot (Trợ lý Dữ liệu). Bạn có thể yêu cầu tôi truy xuất dữ liệu, tôi sẽ phân tích và trả về file CSV cho bạn xem trực tiếp!' 
    }
  ]);
  const messagesEndRef = useRef(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isOpen]);

  const parseCSV = (csvText) => {
    const lines = csvText.split('\n').filter(line => line.trim() !== '');
    if (lines.length === 0) return { headers: [], rows: [] };
    const headers = lines[0].split(',');
    const rows = lines.slice(1).map(line => line.split(','));
    return { headers, rows };
  };

  const handleSend = async () => {
    if (!inputVal.trim() || isLoading) return;
    
    const userMsg = inputVal.trim();
    // Thêm tin nhắn của User
    setMessages(prev => [...prev, { id: Date.now(), role: 'user', type: 'text', content: userMsg }]);
    setInputVal('');
    setIsLoading(true);

    try {
      // Gọi API Chat thực tế
      const res = await chatApi.sendMessage(userMsg);
      
      const botMsgId = Date.now() + 1;
      
      let botMsg = {
        id: botMsgId,
        role: 'bot',
        type: 'text',
        content: res.message
      };

      if (res.file_id) {
        botMsg.fileId = res.file_id;
        botMsg.csvData = null; 
        botMsg.isParsing = false;
        botMsg.isExpanded = false;
      }
      
      setMessages(prev => [...prev, botMsg]);

    } catch (error) {
      setMessages(prev => [...prev, {
        id: Date.now() + 2,
        role: 'bot',
        type: 'text',
        content: '❌ Đã có lỗi xảy ra khi kết nối tới hệ thống AI Copilot. Vui lòng thử lại.'
      }]);
    } finally {
      setIsLoading(false);
    }
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

      {/* Sidebar Drawer */}
      <div className={`fixed top-0 right-0 h-full w-[450px] bg-white shadow-2xl z-50 transform transition-transform duration-300 ease-in-out flex flex-col ${isOpen ? 'translate-x-0' : 'translate-x-full'} border-l border-gray-100`}>
        
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

                {/* Tin nhắn text chính */}
                {msg.role === 'bot' && (
                  <div className="bg-white border border-gray-100 text-gray-700 px-4 py-3 rounded-2xl rounded-tl-sm shadow-sm text-sm leading-relaxed mb-1">
                    {msg.content}
                  </div>
                )}

                {/* Giao diện đính kèm File CSV (Optional) */}
                {msg.role === 'bot' && msg.fileId && (
                  <div className="bg-white border border-gray-200 rounded-xl overflow-hidden shadow-sm mt-2 max-w-[90%]">
                    
                    {/* File Header */}
                    <div className="bg-indigo-50/50 px-3 py-2.5 flex items-center justify-between border-b border-indigo-100">
                      <div className="flex items-center gap-2">
                        <FileText className="w-4 h-4 text-indigo-600" />
                        <span className="text-xs font-semibold text-indigo-900 truncate">Result_{msg.fileId.substring(0,6)}.csv</span>
                      </div>
                      <div className="flex gap-2">
                        <button 
                          onClick={() => {
                            if (!msg.isExpanded) {
                              // Gọi hàm load CSV nếu chưa load
                              if (!msg.csvData) {
                                setMessages(prev => prev.map(m => 
                                  m.id === msg.id ? { ...m, isParsing: true, isExpanded: true } : m
                                ));
                                chatApi.fetchCsvData(msg.fileId).then(csvText => {
                                  const parsed = parseCSV(csvText);
                                  setMessages(prev => prev.map(m => 
                                    m.id === msg.id ? { ...m, isParsing: false, csvData: parsed } : m
                                  ));
                                }).catch(err => {
                                  console.error(err);
                                  setMessages(prev => prev.map(m => 
                                    m.id === msg.id ? { ...m, isParsing: false } : m
                                  ));
                                });
                              } else {
                                setMessages(prev => prev.map(m => 
                                  m.id === msg.id ? { ...m, isExpanded: true } : m
                                ));
                              }
                            } else {
                              setMessages(prev => prev.map(m => 
                                m.id === msg.id ? { ...m, isExpanded: false } : m
                              ));
                            }
                          }}
                          className="flex items-center gap-1.5 px-2.5 py-1.5 bg-white border border-indigo-200 text-indigo-600 rounded hover:bg-indigo-50 transition-colors text-[10px] font-semibold"
                        >
                          <Database className="w-3 h-3" />
                          {msg.isExpanded ? 'ĐÓNG' : 'XEM TRƯỚC'}
                        </button>
                        <a 
                          href={chatApi.getDownloadUrl(msg.fileId)}
                          download
                          className="flex items-center gap-1.5 px-2.5 py-1.5 bg-indigo-600 text-white rounded hover:bg-indigo-700 transition-colors text-[10px] font-semibold"
                          title="Tải file CSV"
                        >
                          <Download className="w-3 h-3" />
                          TẢI XUỐNG
                        </a>
                      </div>
                    </div>
                    
                    {/* CSV Table Preview (Chỉ hiện khi isExpanded = true) */}
                    {msg.isExpanded && (
                      <div className="overflow-x-auto max-h-60 bg-white">
                        {msg.isParsing ? (
                          <div className="flex flex-col items-center justify-center py-6 text-indigo-400">
                            <Loader2 className="w-5 h-5 animate-spin mb-2" />
                            <span className="text-[10px] uppercase font-bold tracking-wider">Đang trích xuất dữ liệu...</span>
                          </div>
                        ) : msg.csvData && msg.csvData.headers.length > 0 ? (
                          <table className="w-full text-left border-collapse">
                            <thead>
                              <tr className="bg-gray-50 text-[10px] text-gray-500 uppercase tracking-wider sticky top-0 shadow-sm">
                                {msg.csvData.headers.map((header, idx) => (
                                  <th key={idx} className="px-3 py-2 border-b border-gray-200 font-semibold whitespace-nowrap">
                                    {header}
                                  </th>
                                ))}
                              </tr>
                            </thead>
                            <tbody className="text-xs text-gray-700 font-medium">
                              {msg.csvData.rows.map((row, rIdx) => (
                                <tr key={rIdx} className="hover:bg-gray-50 border-b border-gray-100 last:border-0">
                                  {row.map((cell, cIdx) => (
                                    <td key={cIdx} className="px-3 py-2 whitespace-nowrap">
                                      {cell}
                                    </td>
                                  ))}
                                </tr>
                              ))}
                            </tbody>
                          </table>
                        ) : (
                          <div className="py-4 text-center text-xs text-gray-500">
                            Không thể hiển thị xem trước dữ liệu
                          </div>
                        )}
                      </div>
                    )}
                    
                    {msg.isExpanded && msg.csvData && !msg.isParsing && (
                      <div className="bg-gray-50 px-3 py-1.5 border-t border-gray-100 text-[10px] font-medium text-gray-500 flex justify-between">
                        <span>Đã tải xong {msg.csvData.rows.length} dòng dữ liệu</span>
                      </div>
                    )}
                  </div>
                )}
              </div>
            </div>
          ))}
          
          {isLoading && (
            <div className="flex justify-start">
              <div className="flex-shrink-0 w-8 h-8 rounded-full bg-indigo-100 flex items-center justify-center border border-indigo-200 mr-3 mt-1">
                <Sparkles className="w-4 h-4 text-indigo-600 animate-pulse" />
              </div>
              <div className="bg-white border border-gray-100 text-gray-500 px-4 py-3 rounded-2xl rounded-tl-sm shadow-sm flex items-center gap-2">
                <div className="flex gap-1">
                  <span className="w-1.5 h-1.5 bg-indigo-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></span>
                  <span className="w-1.5 h-1.5 bg-indigo-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></span>
                  <span className="w-1.5 h-1.5 bg-indigo-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></span>
                </div>
              </div>
            </div>
          )}
          
          <div ref={messagesEndRef} />
        </div>

        {/* Input Area */}
        <div className="p-4 bg-white border-t border-gray-100">
          <div className="relative flex items-end bg-gray-50 border border-gray-200 rounded-xl focus-within:ring-2 focus-within:ring-indigo-100 focus-within:border-indigo-400 transition-all shadow-inner">
            <textarea
              value={inputVal}
              onChange={(e) => setInputVal(e.target.value)}
              onKeyDown={handleKeyDown}
              disabled={isLoading}
              placeholder="Gõ lệnh SQL hoặc đặt câu hỏi yêu cầu dữ liệu..."
              className="w-full bg-transparent border-none focus:ring-0 resize-none text-sm p-3 min-h-[44px] max-h-[120px] outline-none text-gray-800 placeholder-gray-400 disabled:opacity-50"
              rows={1}
            />
            <button 
              onClick={handleSend}
              disabled={!inputVal.trim() || isLoading}
              className="p-2 m-1.5 text-white bg-indigo-600 rounded-lg hover:bg-indigo-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex-shrink-0"
            >
              {isLoading ? <Loader2 className="w-4 h-4 animate-spin" /> : <Send className="w-4 h-4" />}
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
