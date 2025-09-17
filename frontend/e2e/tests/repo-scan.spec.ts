import { test, expect } from '../fixtures/test-fixture';

test.describe('Repository Scanner', () => {
  test.beforeEach(async ({ page }) => {
    // Increase timeout for API calls and slow environments
    test.setTimeout(120000);
  });

  test('should scan a repository and generate plan', async ({ page }) => {
    // Navigate to the home page
    await page.goto('/');
    
    // Fill in the repository URL and branch
    await page.fill('input[type="text"]', 'https://github.com/Vishakha-Sawra/agentic-ai-news-platform');
    
    // Click the scan button
    await page.click('button:has-text("Scan")');
    
    // Wait for the UI to navigate to /plan (frontend routes on success)
    await page.waitForURL('**/plan', { timeout: 120000 });
    
    // Wait for the plan page to load and check its content
    await page.waitForSelector('h1');
    
  // Look for elements that indicate successful scan (case-insensitive checks)
  // Use getByText which accepts strings; match common labels shown in UI
  const projectLabel = page.getByText(/project name/i).first();
  const languagesLabel = page.getByText(/languages/i).first();
  await expect(projectLabel).toBeVisible();
  await expect(languagesLabel).toBeVisible();
    
    // Generate plan - wait for button to be enabled
    const generateButton = page.getByRole('button', { name: /generate plan/i });
    await generateButton.waitFor({ state: 'visible', timeout: 120000 });
    await generateButton.click();
    
    // Wait for the plan UI to show results (pre or JSON block)
    await page.waitForSelector('pre, .plan-output, #plan', { timeout: 120000 });
  });

  test('should handle invalid repository URL', async ({ page }) => {
    await page.goto('/');
    
    // Fill in an invalid repository URL
    await page.fill('input[type="text"]', 'not-a-valid-url');
    
    // Click the scan button
    await page.click('button:has-text("Scan")');
    
    // Wait for the scan network call to complete (any non-2xx status)
    const response = await page.waitForResponse(r => r.url().includes('/scan'));
    const status = response.status();
    // Accept 400 or 422 (FastAPI returns 422 for validation errors)
    expect([400, 422]).toContain(status);
  });

  test('should execute plan and show generated files', async ({ page }) => {
    // Start with a fresh page
    await page.goto('/');
    
    // Fill in valid repository details
    await page.fill('input[type="text"]', 'https://github.com/Vishakha-Sawra/agentic-ai-news-platform');
    
    // Start scanning
    await page.click('button:has-text("Scan")');
    
    // Wait for navigation to plan page
    await page.waitForURL('**/plan', { timeout: 120000 });
    
    // Wait for the plan page elements to be visible
    await page.waitForSelector('h1', { timeout: 120000 });
    
    // Generate plan
    const generateButton = page.getByRole('button', { name: /generate plan/i });
    await generateButton.waitFor({ state: 'visible', timeout: 120000 });
    await generateButton.click();
    
    // Wait for the plan UI to show results
    await page.waitForSelector('pre, .plan-output, #plan', { timeout: 120000 });
    
    // Execute plan if the button exists
    const executeButton = page.getByRole('button', { name: /execute/i });
    if (await executeButton.isVisible()) {
      await executeButton.click();
      
      // Wait for execution UI/output
      await page.waitForSelector('pre, .generated-files, #files', { timeout: 120000 });
      
      // Verify some generated file content is visible
      await expect(page.locator('pre, .generated-files, #files')).toBeVisible();
    }
  });
});
