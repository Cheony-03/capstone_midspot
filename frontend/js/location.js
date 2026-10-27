window.updateRadiusText = function(value) {
  const n = Number(value);
  document.getElementById('radiusValueText').textContent = n < 1000 ? `${n}m` : `${(n / 1000).toFixed(1)} km`;
};
updateRadiusText(document.getElementById('searchRadiusRange').value);
let selectedMember = null;
async function updateParticipantUI() {
  const container = document.getElementById('participantListContainer');
  try {
    const members = await MidspotAPI.getParticipants(Midspot.requireRoom());
    // 서버에 정원 필드가 없으므로 원본의 고정 /3은 사용하지 않습니다.
    document.getElementById('participantCount').textContent = `${members.length}명 등록 완료`;
    container.replaceChildren();
    if (!members.length) container.textContent = '아직 저장된 멤버가 없습니다.';
    for (const p of members) {
      const card = document.createElement('div'); card.className = 'participant-card';
      const header = document.createElement('div'); header.className = 'card-header'; header.textContent = `👤 ${p.nickname}`;
      const body = document.createElement('div'); body.className = 'card-body';
      body.textContent = `📍 ${p.address_name} / 선호 카테고리: 조회 API 연결 대기`;
      card.append(header, body); container.append(card);
    }
    selectedMember = members.find(p => p.participant_id === Midspot.participant) || null;
    if (Midspot.participant && !selectedMember) throw new Error('참여자 정보가 없습니다. 참여자 등록 페이지에서 다시 입장해주세요.');
    if (selectedMember) {
      document.getElementById('userName').value = selectedMember.nickname;
      document.getElementById('userAddress').value = selectedMember.address_name;
    }
    return members;
  } catch (error) { Midspot.failedList(container, error); throw error; }
}
document.getElementById('saveParticipantBtn').addEventListener('click', () => Midspot.busy(document.getElementById('saveParticipantBtn'), async () => {
  Midspot.requireRoom();
  if (!selectedMember) throw new Error('먼저 참여자 등록 페이지에서 참여해주세요.');
  if (document.getElementById('userName').value.trim() !== selectedMember.nickname || document.getElementById('userAddress').value.trim() !== selectedMember.address_name) {
    throw new Error('출발지·이름 수정 API가 없어 변경사항을 저장할 수 없습니다. 카테고리 투표 API도 아직 제공되지 않았습니다.');
  }
  const categories = Array.from(document.querySelectorAll('input[name="prefCategory"]:checked'), el => el.value);
  if (!categories.length) throw new Error('선호 카테고리를 최소 1개 선택해주세요.');
  // 요청 필드명은 미확정입니다. 어댑터에 전달만 하며 현재는 명확한 미구현 오류를 표시합니다.
  await MidspotAPI.saveCategoryVote(Midspot.room, Midspot.participant, categories);
}));
document.getElementById('goToResultBtn').addEventListener('click', () => Midspot.busy(document.getElementById('goToResultBtn'), async () => {
  const members = await updateParticipantUI();
  if (members.length < 2) throw new Error('중간지점 계산에는 최소 2명의 참여자가 필요합니다.');
  alert('아직 카테고리 투표·추천 장소 API가 없어 결과 페이지에는 참여자 출발지만 표시합니다.');
  location.assign(Midspot.url('result.html', {radius: document.getElementById('searchRadiusRange').value}));
}));
updateParticipantUI().catch(() => {});
