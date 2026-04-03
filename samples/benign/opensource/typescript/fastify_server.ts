// Source: TypeScript Benign Sample
// Generated: 2026-04-02 11:48:04.520162

#!/usr/bin/env ts-node
/**
 * Fastify 服务器 - 良性
 */
import Fastify from 'fastify';

const fastify = Fastify({ logger: true });

fastify.get('/', async (request, reply) => {
  return { hello: 'world' };
});

const start = async () => {
  try {
    await fastify.listen({ port: 3000 });
  } catch (err) {
    fastify.log.error(err);
    process.exit(1);
  }
};

start();
