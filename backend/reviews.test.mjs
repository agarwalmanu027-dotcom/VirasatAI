import test from 'node:test';
import assert from 'node:assert/strict';
import { AuthStore } from './auth.mjs';
import { ReviewStore } from './reviews.mjs';

test('reviews require login, validate places and ratings, update instead of duplicating', () => {
  const auth = new AuthStore();
  try {
    const reviews = new ReviewStore(auth);
    const { token } = auth.register({ email: 'test@example.com', displayName: 'Tester', password: 'test-password-123' });
    assert.throws(() => reviews.save(null, 'taj_mahal', { rating: 5 }));
    assert.throws(() => reviews.save(token, 'unknown', { rating: 5 }));
    assert.throws(() => reviews.save(token, 'taj_mahal', { rating: 6 }));
    reviews.save(token, 'taj_mahal', { rating: 5 });
    reviews.save(token, 'taj_mahal', { rating: 3, comment: 'Updated review' });
    const result = reviews.list('taj_mahal');
    assert.equal(result.count, 1);
    assert.equal(result.average, 3);
    assert.equal(result.reviews[0].comment, 'Updated review');
    assert.equal(result.reviews[0].email, undefined);
    assert.deepEqual(reviews.mine(token).reviews.map((item) =>
      [item.placeId, item.rating, item.comment]),
      [['taj_mahal', 3, 'Updated review']]);
  } finally { auth.close(); }
});
