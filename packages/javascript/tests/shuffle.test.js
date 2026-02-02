/**
 * Tests for wickit-js shuffle module
 */

const { discoverService, ServiceDiscoveryError } = require('../shuffle');

describe('Service Discovery', () => {
  test('should discover service on valid port', async () => {
    // Mock successful fetch
    global.fetch = jest.fn(() =>
      Promise.resolve({
        ok: true,
        json: () => Promise.resolve({
          service: 'test-service',
          status: 'healthy',
          port: 7777
        })
      })
    );

    const service = await discoverService({
      serviceId: 'test-service',
      portRange: [7777, 7778],
      timeout: 1000
    });

    expect(service).toBeDefined();
    expect(service.port).toBe(7777);
    expect(service.health.service).toBe('test-service');
  });

  test('should throw error when service not found', async () => {
    global.fetch = jest.fn(() => Promise.reject(new Error('Connection refused')));

    await expect(
      discoverService({
        serviceId: 'nonexistent',
        portRange: [9999, 9999],
        timeout: 100
      })
    ).rejects.toThrow(ServiceDiscoveryError);
  });

  test('should verify service ID matches', async () => {
    global.fetch = jest.fn(() =>
      Promise.resolve({
        ok: true,
        json: () => Promise.resolve({
          service: 'wrong-service',
          status: 'healthy'
        })
      })
    );

    await expect(
      discoverService({
        serviceId: 'expected-service',
        portRange: [7777, 7777],
        timeout: 100
      })
    ).rejects.toThrow('Service ID mismatch');
  });
});

describe('ServiceDiscoveryError', () => {
  test('should create error with correct name', () => {
    const error = new ServiceDiscoveryError('Test error');
    expect(error.name).toBe('ServiceDiscoveryError');
    expect(error.message).toBe('Test error');
  });
});
