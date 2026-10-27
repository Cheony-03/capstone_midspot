window.MidspotKakao = (() => {
  let loading;
  function load() {
    if (window.kakao?.maps?.services) return Promise.resolve(window.kakao);
    if (loading) return loading;
    loading = new Promise((resolve, reject) => {
      const script = document.createElement('script');
      const timer = setTimeout(() => fail(), 20000);
      function fail() { clearTimeout(timer); script.remove(); loading = null; reject(new Error('카카오 지도를 불러오지 못했습니다. JavaScript 키, 카카오맵 사용 설정, 등록 웹 도메인 및 네트워크를 확인해주세요.')); }
      script.src = 'https://dapi.kakao.com/v2/maps/sdk.js?autoload=false&libraries=services&appkey=' + encodeURIComponent(window.MIDSPOT_CONFIG.kakaoJavaScriptKey);
      script.onerror = fail;
      script.onload = () => {
        if (!window.kakao?.maps) return fail();
        window.kakao.maps.load(() => {
          clearTimeout(timer);
          if (!window.kakao.maps.services) return fail();
          resolve(window.kakao);
        });
      };
      document.head.appendChild(script);
    });
    return loading;
  }
  async function geocode(address) {
    const kakao = await load();
    return new Promise((resolve, reject) => {
      const timer = setTimeout(() => reject(new Error('주소 좌표 변환 시간이 초과되었습니다.')), 15000);
      new kakao.maps.services.Geocoder().addressSearch(address, (results, status) => {
        clearTimeout(timer);
        if (status !== kakao.maps.services.Status.OK || !results.length) return reject(new Error('선택한 주소의 좌표를 찾지 못했습니다. 주소를 다시 검색해주세요.'));
        const latitude = Number(results[0].y), longitude = Number(results[0].x);
        if (!Number.isFinite(latitude) || !Number.isFinite(longitude)) return reject(new Error('좌표 응답이 올바르지 않습니다.'));
        resolve({latitude, longitude});
      });
    });
  }
  return {load, geocode};
})();

window.execDaumPostcode = function () {
  if (!window.daum?.Postcode) return alert('주소 검색을 불러오지 못했습니다. 네트워크를 확인하고 새로고침해주세요.');
  new daum.Postcode({oncomplete(data) {
    document.getElementById('userAddress').value = data.userSelectedType === 'R' ? data.roadAddress : data.jibunAddress;
  }}).open();
};
