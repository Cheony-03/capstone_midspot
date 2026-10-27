const createButton = document.getElementById('createRoomBtn');
let createdInvite = '';
createButton.addEventListener('click', () => Midspot.busy(createButton, async () => {
  if (createdInvite) { location.assign(createdInvite); return; }
  const room = await MidspotAPI.createRoom();
  if (!room.room_id) throw new Error('방 생성 응답에 room_id가 없습니다.');
  const invite = new URL('page2.html', location.href);
  invite.searchParams.set('room', room.room_id);
  createdInvite = invite.href;
  document.getElementById('inviteLinkInput').value = createdInvite;
  document.getElementById('shareSection').style.display = 'block';
  createButton.textContent = '생성된 모임 입장하기';
}));
document.getElementById('copyLinkBtn').addEventListener('click', () => Midspot.busy(document.getElementById('copyLinkBtn'), async () => {
  const input = document.getElementById('inviteLinkInput');
  if (!input.value) throw new Error('먼저 모임을 만들어주세요.');
  try { await navigator.clipboard.writeText(input.value); }
  catch (_) { input.focus(); input.select(); throw new Error('자동 복사가 불가능합니다. 선택된 초대 링크를 직접 복사해주세요.'); }
  alert('초대 링크를 복사했습니다.');
}));
