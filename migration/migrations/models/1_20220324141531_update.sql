-- upgrade --
ALTER TABLE "sub" RENAME COLUMN "at" TO "dynamic_at";
-- downgrade --
ALTER TABLE "sub" RENAME COLUMN "dynamic_at" TO "at";
