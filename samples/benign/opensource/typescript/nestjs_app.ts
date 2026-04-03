// Source: TypeScript Benign Sample
// Generated: 2026-04-02 11:48:04.520124

#!/usr/bin/env ts-node
/**
 * NestJS Web 应用 - 良性
 */
import { NestFactory } from '@nestjs/core';
import { Controller, Get, Module } from '@nestjs/common';

@Controller()
class AppController {
  @Get()
  getHello(): string {
    return 'Hello World!';
  }
}

@Module({
  controllers: [AppController],
})
class AppModule {}

async function bootstrap() {
  const app = await NestFactory.create(AppModule);
  await app.listen(3000);
  console.log('Server running on port 3000');
}

bootstrap();
