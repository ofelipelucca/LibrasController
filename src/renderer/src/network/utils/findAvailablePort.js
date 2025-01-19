const net = require('net');

module.exports = async function findAvailablePort(start, end) {
    return new Promise((resolve, reject) => {
        const port = start;
        const server = net.createServer();
        server.listen(port, () => {
            server.close(() => resolve(port));
        });
        server.on('error', () => {
            if (port < end) {
                resolve(findAvailablePort(port + 1, end));
            } else {
                reject(new Error(`Nao foi possivel encontrar uma porta disponivel no intervalo ${start} a ${end}.`));
            }
        });
    });
}