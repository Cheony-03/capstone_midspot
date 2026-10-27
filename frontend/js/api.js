/* 현재 제공된 FastAPI 라우트만 호출합니다. 미구현 경로를 추측하지 않습니다. */
window.MidspotAPI = (() => {
  async function request(path, options = {}) {
    const base = window.MIDSPOT_CONFIG.apiBaseUrl.trim().replace(/\/+$/, '');
    if (!base) throw new Error('아직 서버 주소가 설정되지 않았습니다. js/config.js의 apiBaseUrl을 설정해주세요.');
    const controller = new AbortController();
    const timer = setTimeout(() => controller.abort(), window.MIDSPOT_CONFIG.timeoutMs);
    try {
      const response = await fetch(base + path, {
        ...options, signal: controller.signal,
        headers: { ...(options.body ? {'Content-Type': 'application/json'} : {}), ...options.headers }
      });
      const text = await response.text();
      let data = null;
      if (text) { try { data = JSON.parse(text); } catch (_) { /* 오류 처리에서 사용 */ } }
      if (!response.ok) {
        const detail = data?.detail;
        const msg = Array.isArray(detail)
          ? detail.map(d => `${(d.loc || []).join('.')}: ${d.msg}`).join('\n')
          : typeof detail === 'string' ? detail : `요청 실패 (HTTP ${response.status})`;
        throw new Error(msg);
      }
      if (data === null) throw new Error('서버에서 올바른 JSON 응답을 받지 못했습니다. 서버 주소를 확인해주세요.');
      return data;
    } catch (error) {
      if (error.name === 'AbortError') throw new Error('서버 응답 시간이 초과되었습니다.');
      if (error instanceof TypeError) throw new Error('서버에 연결할 수 없습니다. 서버 실행 여부, 주소, CORS 및 HTTPS 설정을 확인해주세요.');
      throw error;
    } finally { clearTimeout(timer); }
  }
  const roomPath = id => `/rooms/${encodeURIComponent(id)}`;
  return Object.freeze({
    createRoom: () => request('/rooms', {method:'POST'}),
    getRoom: id => request(roomPath(id)),
    addParticipant: (id, participant) => request(roomPath(id) + '/participants', {method:'POST', body:JSON.stringify(participant)}),
    getParticipants: id => request(roomPath(id) + '/participants'),
    // 아래 두 함수의 본문만 실제 명세를 받은 뒤 구현합니다. 현재는 네트워크 요청/저장을 하지 않습니다.
    saveCategoryVote: async () => { throw new Error('카테고리 투표 저장 API가 아직 제공되지 않았습니다. 선택 내용은 서버에 저장되지 않았습니다.'); },
    getCategoryVotes: async () => { throw new Error('카테고리 투표 조회 API가 아직 제공되지 않았습니다.'); },
    getPlaces: async () => { throw new Error('추천 장소 목록 API가 아직 제공되지 않았습니다.'); }
  });
})();
