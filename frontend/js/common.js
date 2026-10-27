window.Midspot = (() => {
  const params = new URLSearchParams(location.search);
  const room = params.get('room');
  let participant = params.get('participant');
  function requireRoom() {
    if (!room) throw new Error('방 ID가 없습니다. 모임 만들기 또는 초대 링크로 입장해주세요.');
    return room;
  }
  function url(page, extra = {}) {
    const target = new URL(page, location.href);
    if (room) target.searchParams.set('room', room);
    if (participant) target.searchParams.set('participant', participant);
    for (const [key, value] of Object.entries(extra)) if (value != null) target.searchParams.set(key, value);
    return target.href;
  }
  async function busy(button, action) {
    if (button?.disabled) return;
    if (button) button.disabled = true;
    try { await action(); } catch (error) { alert(error.message || '처리 중 오류가 발생했습니다.'); }
    finally { if (button) button.disabled = false; }
  }
  function setParticipant(id) {
    participant = id;
    const current = new URL(location.href);
    current.searchParams.set('participant', id);
    history.replaceState(null, '', current);
  }
  async function register() {
    const nickname = document.getElementById('userName').value.trim();
    const address_name = document.getElementById('userAddress').value.trim();
    if (!nickname || !address_name) throw new Error('이름과 출발지를 모두 입력해주세요.');
    if (nickname.length > 20) throw new Error('닉네임은 20자 이하로 입력해주세요.');
    const id = requireRoom();
    // 서버 주소가 없을 때 불필요하게 외부 좌표 API부터 호출하지 않습니다.
    if (!window.MIDSPOT_CONFIG.apiBaseUrl.trim()) throw new Error('아직 서버 주소가 설정되지 않았습니다. js/config.js의 apiBaseUrl을 설정해주세요.');
    const coords = await MidspotKakao.geocode(address_name);
    const saved = await MidspotAPI.addParticipant(id, {nickname, address_name, ...coords});
    if (!saved.participant_id) throw new Error('참여자 등록 응답에 participant_id가 없습니다.');
    setParticipant(saved.participant_id);
    return saved;
  }
  function failedList(container, error) { container.textContent = `목록 조회 실패: ${error.message}`; }
  return {room, get participant() {return participant;}, requireRoom, url, busy, setParticipant, register, failedList};
})();
