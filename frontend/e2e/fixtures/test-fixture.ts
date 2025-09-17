import { test as base } from '@playwright/test';

export type TestFixtures = {
  repoUrl: string;
};

export const test = base.extend<TestFixtures>({
  repoUrl: ['https://github.com/example/test-repo', { option: true }],
});

export { expect } from '@playwright/test';
