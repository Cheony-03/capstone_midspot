// 예시 장소를 실제 추천 결과로 오인하지 않도록 서버 데이터 대신 노출하지 않습니다.
const placeList = document.getElementById('voteList');
placeList.textContent = '추천 장소 목록 API 연결 대기 — 아직 추천 결과가 없습니다.';
window.submitVotes = () => alert('장소 투표 API는 아직 연결되지 않았습니다. 투표가 저장되지 않았습니다.');
window.decidePlace = () => alert('최종 장소 확정 API는 아직 연결되지 않았습니다. 장소가 확정되지 않았습니다.');
window.shareLocation = () => Midspot.busy(document.querySelector('button[onclick="shareLocation()"]'), async () => {
  Midspot.requireRoom();
  const share = new URL('result.html', location.href);
  share.searchParams.set('room', Midspot.room);
  // 개인 참여자 식별자는 공유 링크에 넣지 않습니다.
  try { await navigator.clipboard.writeText(share.href); }
  catch (_) { throw new Error('링크 자동 복사에 실패했습니다. HTTPS 또는 localhost에서 실행해주세요.'); }
  alert('결과 페이지 링크를 복사했습니다. 아직 확정된 장소는 없습니다.');
});
(async () => {
  const container = document.getElementById('map');
  try {
    Midspot.requireRoom();
    container.textContent = '참여자 위치를 불러오는 중입니다…';
    const members = await MidspotAPI.getParticipants(Midspot.room);
    const points = members.filter(p => Number.isFinite(p.latitude) && Number.isFinite(p.longitude) && Math.abs(p.latitude) <= 90 && Math.abs(p.longitude) <= 180);
    if (!points.length) throw new Error('표시할 참여자 좌표가 없습니다.');
    const kakao = await MidspotKakao.load();
    container.replaceChildren();
    const map = new kakao.maps.Map(container, {center:new kakao.maps.LatLng(points[0].latitude, points[0].longitude), level:5});
    const bounds = new kakao.maps.LatLngBounds();
    for (const p of points) {
      const position = new kakao.maps.LatLng(p.latitude, p.longitude);
      new kakao.maps.Marker({map, position, title:p.nickname});
      bounds.extend(position);
    }
    if (points.length > 1) map.setBounds(bounds);
    // midpoint.py는 HTTP API가 아니므로 임의 호출하거나 클라이언트 계산을 서버 결과로 표시하지 않습니다.
  } catch (error) { container.textContent = error.message; }
})();
