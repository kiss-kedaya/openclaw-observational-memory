const axios = require('axios');

const MEMORY_API = 'http://localhost:3000/api';

module.exports = {
  name: 'observational-memory',
  
  async onMessage(event, context) {
    try {
      const { sessionId, message, role } = event;
      
      // 创建或更新会话
      await axios.post(`${MEMORY_API}/sessions`, {
        session_id: sessionId,
        messages: [{
          role: role || 'user',
          content: message,
          timestamp: new Date().toISOString()
        }]
      }, { timeout: 5000 });
      
      context.log('OK - Message recorded:', sessionId);
      
    } catch (error) {
      if (error.code === 'ECONNREFUSED') {
        context.log('WARN - Observational Memory service not running');
      } else {
        context.log('ERROR -', error.message);
      }
    }
  },
  
  async onSessionEnd(event, context) {
    try {
      const { sessionId } = event;
      
      // 获取观察记录
      const response = await axios.get(`${MEMORY_API}/observations/${sessionId}`, {
        timeout: 5000
      });
      
      context.log(`INFO - Session ${sessionId} has ${response.data.length} observations`);
      
    } catch (error) {
      context.log('ERROR -', error.message);
    }
  }
};
