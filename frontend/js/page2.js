let participants = [];
async function updateParticipantUI() {
  const list = document.getElementById('participantList');
  try {
    participants = await MidspotAPI.getParticipants(Midspot.requireRoom());
    document.getElementById('participantCount').textContent = participants.length;
    list.replaceChildren();
    if (!participants.length) { list.textContent = '아직 참여한 사람이 없습니다.'; return; }
    participants.forEach((p, i) => {
      const li = document.createElement('li');
      li.style.cssText = 'padding:8px 0;border-bottom:1px solid #eee;';
      const strong = document.createElement('strong');
      strong.textContent = `${i + 1}. ${p.nickname}`;
      li.append(strong, document.createTextNode(` (${p.address_name})`));
      list.appendChild(li);
    });
  } catch (error) { Midspot.failedList(list, error); throw error; }
}
window.addParticipant = function(event) {
  event.preventDefault();
  const button = document.querySelector('#participantForm button[type="submit"]');
  return Midspot.busy(button, async () => {
    if (Midspot.participant) throw new Error('이 브라우저 탭에서는 이미 참여했습니다. 카테고리 선택으로 이동해주세요. 출발지 수정 API는 아직 없습니다.');
    await Midspot.register();
    alert('출발지가 서버에 등록되었습니다.');
    await updateParticipantUI();
  });
};
window.goToNextStep = function() {
  const button = document.querySelector('button[onclick="goToNextStep()"]');
  return Midspot.busy(button, async () => {
    await updateParticipantUI();
    if (!Midspot.participant || !participants.some(p => p.participant_id === Midspot.participant)) throw new Error('먼저 본인의 참여 정보를 등록해주세요.');
    location.assign(Midspot.url('location.html'));
  });
};
updateParticipantUI().catch(() => {});
