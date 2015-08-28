var panoClient;

function panoRunner() {
  init();
  animate(0);
}

function getConfig(key, def) {
  key = key.replace(/[\[]/, "\\[").replace(/[\]]/, "\\]");
  var regex = new RegExp("[\\?&]" + key + "=([^&#]*)"),
      results = regex.exec(location.search);
  return results === null ? def : decodeURIComponent(results[1].replace(/\+/g, " "));
}

function init() {
  var container, vertFov, aspectRatio;
  var yawRads, pitchRads, rollRads, isLeader;
  var ros = new ROSLIB.Ros({ url: 'ws://localhost:9090' });

  container = document.getElementById( 'container' );

  vertFov = getConfig('fov', 75) * 1.0;
  aspectRatio = window.innerWidth / window.innerHeight;
  yawRads = aspectRatio * toRad(vertFov * getConfig('yawOffset', 0));
  pitchRads = toRad(getConfig('pitchOffset', 0) * 1.0);
  rollRads = toRad(getConfig('rollOffset', 0) * 1.0);
  isLeader = getConfig('leader', 'false').toLowerCase() == "true";

  panoClient = new PanoClient(ros, vertFov, aspectRatio, yawRads, pitchRads,
      rollRads, isLeader);

  container.appendChild(panoClient.getDomElement());

  window.addEventListener('resize', onWindowResize, false);
}

function onWindowResize() {
  panoClient.windowResize();
}

function animate(nowMsec) {
  requestAnimationFrame(animate);
  panoClient.update(nowMsec);
}

function toRad(deg) {
  return THREE.Math.degToRad(deg);
}

window.onload = panoRunner;
