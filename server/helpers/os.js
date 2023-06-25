function getPodpy() {
    const isWin = process.platform === "win32";
    return isWin ? "pod.bat" : "pod.sh";
}

module.exports = { getPodpy };