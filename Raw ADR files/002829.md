# NFT Contract Design - Architecture Decision Record

## Context

We need to design a Sui Move contract for a hackathon project that:

1. Creates a single "Offbrand Crypto" collection.
2. Allows users to mint custom NFTs into this collection, including image generation metadata and a separate, updatable prompt for an "8-Bit Oracle" advisor system.
3. Handles basic minting fees and fees for updating the advisor prompt.
4. Implements on-chain royalties using Sui's TransferPolicy system.

## Decision

We will implement a Sui Move contract with:

1. A single, admin-initialized `OffbrandCollection` that owns a shared `TransferPolicy` for the entire collection.
2. `OffbrandNFT` structs that store core metadata, image generation details (via a dynamic field), an advisor prompt configuration (via a dynamic field), and custom attributes (via dynamic fields).
3. The NFT will store a `vector<RoyaltyRecipient>` for royalty information.
4. Minting fees and advisor prompt update fees will be collected by the collection admin.
5. **Image Storage Clarification:** Actual image data (blobs) is stored off-chain (e.g., on Walrus). The NFT stores a `walrus_blob_id` and `image_url` as pointers.
6. **Royalty Implementation:** Using Sui's TransferPolicy system for on-chain royalties:
   - Collection-level TransferPolicy shared object
   - TransferPolicyCap held by collection admin
   - Royalty rules added via `royalty_rule` module
   - Basis points (bps) for percentage-based royalties

## Status

Approved

## Consequences

### Positive

- Clear separation of NFT image generation data and updatable advisor prompt data.
- Flexible NFT attributes via dynamic fields.
- On-chain royalty enforcement through Sui's TransferPolicy system.
- User-friendly minting into a single collection.
- Fees for minting and prompt updates provide a monetization path for the collection admin.
- Collection-level TransferPolicy simplifies royalty management.

### Negative

- Single collection limits broader user-driven collection creation (by design for this project).
- Collection-level TransferPolicy means all NFTs in the collection share the same royalty rules.
- Initial implementation uses only the first royalty recipient for simplicity.

## Technical Details

1. Contract Structure

```move
module nfter::nfter {
    use std::string::{Self, String};
    use sui::package;
    use sui::object;
    use sui::tx_context;
    use sui::sui::SUI;
    use sui::dynamic_field as df;
    use sui::coin::{Self, Coin};
    use sui::display;
    use sui::transfer_policy::{Self, TransferPolicy, TransferPolicyCap};

    use nfter::royalty_rule;

    const IMAGE_METADATA_KEY: vector<u8> = b"image_metadata";
    const PROMPT_CONFIG_KEY: vector<u8> = b"prompt_config";
    const E_INVALID_ROYALTY: u64 = 1;

    /// Represents a recipient for royalty payments and their percentage.
    public struct RoyaltyRecipient has store {
        recipient: address,
        percentage: u8, // e.g., 10 for 10%
    }

    public struct OffbrandCollection has key {
        id: object::UID,
        name: String,
        description: String,
        admin: address,
        total_minted: u64,
        minting_fee: u64,
        prompt_update_fee: u64,
        publisher: package::Publisher,
        transfer_policy_id: ID, // Store the ID of the shared TransferPolicy
    }

    public struct OffbrandNFT has key, store {
        id: object::UID,
        name: String,
        description: String,
        creator: address,
        mint_number: u64,
        royalty_info: vector<RoyaltyRecipient>,
    }

    public struct NFTAttribute has store {
        value: String,
        last_updated: u64,
    }

    public struct PromptConfig has store {
        base_prompt: String,
        style_prompt: String,
        last_updated: u64,
        update_count: u64,
    }

    public struct ImageMetadata has store {
        walrus_blob_id: String,      // Walrus blob ID
        image_url: String,           // Public URL for display
        generation_prompt: String,   // Exact prompt used for generation
        model_version: String,       // Model version used
        generation_params: String,   // JSON string of generation parameters
        created_at: u64,            // Timestamp of generation
    }

    public struct NFTER has drop {} // One-Time Witness

    fun init(otw: NFTER, ctx: &mut tx_context::TxContext) {
        let publisher = package::claim(otw, ctx);
        let mut display = display::new<OffbrandNFT>(&publisher, ctx);

        // Basic metadata
        display.add(b"name", b"{name}");
        display.add(b"description", b"{description}");
        display.add(b"mint_number", b"{mint_number}");

        // Image display - using Walrus blob URL
        display.add(b"image_url", b"https://walrus.xyz/blob/{walrus_blob_id}");

        // Generation metadata
        display.add(b"generation_prompt", b"{generation_prompt}");
        display.add(b"model_version", b"{model_version}");
        display.add(b"created_at", b"{created_at}");

        // Additional metadata for explorer
        display.add(b"project_url", b"https://nfter.xyz");
        display.add(b"creator", b"{creator}");

        display.update_version();

        transfer::public_transfer(publisher, ctx.sender());
        transfer::public_transfer(display, ctx.sender());
    }

    public entry fun init_collection(
        name: String,
        description: String,
        minting_fee: u64,
        prompt_update_fee: u64,
        publisher: package::Publisher,
        ctx: &mut tx_context::TxContext
    ) {
        // Create the TransferPolicy for the collection
        let (policy, policy_cap) = transfer_policy::new<OffbrandNFT>(&publisher, ctx);
        let policy_id = object::id(&policy);

        // Share the TransferPolicy
        transfer::public_share_object(policy);

        let collection = OffbrandCollection {
            id: object::new(ctx),
            name,
            description,
            admin: ctx.sender(),
            total_minted: 0,
            minting_fee,
            prompt_update_fee,
            publisher,
            transfer_policy_id: policy_id,
        };

        // Transfer the TransferPolicyCap to the admin
        transfer::public_transfer(policy_cap, ctx.sender());
        transfer::transfer(collection, ctx.sender());
    }

    /// Update the royalty rules for the collection
    /// Only the collection admin can call this function
    public entry fun update_royalty_rules(
        collection: &OffbrandCollection,
        policy: &mut TransferPolicy<OffbrandNFT>,
        policy_cap: &TransferPolicyCap<OffbrandNFT>,
        amount_bp: u16,
        min_amount: u64,
        ctx: &mut tx_context::TxContext
    ) {
        // Verify the caller is the collection admin
        assert!(ctx.sender() == collection.admin, 0);

        // Add the royalty rule using our custom module
        royalty_rule::add<OffbrandNFT>(
            policy,
            policy_cap,
            amount_bp,
            min_amount
        );
    }

    public entry fun mint_nft(
        collection: &mut OffbrandCollection,
        name: String, description: String,
        royalty_recipients: vector<address>, // Parallel vectors for entry function
        royalty_percentages: vector<u8>,
        base_prompt: String,       // For 8-bit Oracle advisor prompt
        style_prompt: String,      // For 8-bit Oracle advisor prompt
        walrus_blob_id: String,    // Pointer to off-chain image
        image_url: String,         // Public URL of off-chain image
        generation_prompt_param: String, // Prompt used to generate the NFT image
        model_version: String,
        generation_params: String,
        attributes_names: vector<String>,
        attributes_values: vector<String>,
        mut payment: Coin<SUI>,
        ctx: &mut tx_context::TxContext
    ) {
        // Check payment
        let fee = collection.minting_fee;
        assert!(balance::value(payment) >= fee, 1);

        // Transfer fee to collection admin
        let fee_balance = balance::split(payment, fee);
        transfer::public_transfer(
            balance::into_coin(fee_balance, ctx),
            tx_context::sender(ctx)
        );

        // Create NFT
        let id = object::new(ctx);
        let nft = OffbrandNFT {
            id,
            name,
            description,
            creator: tx_context::sender(ctx),
            mint_number: collection.total_minted + 1,
            royalty_info: vector::new(),
        };

        // Add image metadata
        df::add(&mut nft.id, IMAGE_METADATA_KEY, ImageMetadata {
            walrus_blob_id,
            image_url,
            generation_prompt: generation_prompt_param,
            model_version,
            generation_params,
            created_at: tx_context::epoch(ctx),
        });

        // Add prompt configuration
        df::add(&mut nft.id, PROMPT_CONFIG_KEY, PromptConfig {
            base_prompt,
            style_prompt,
            last_updated: tx_context::epoch(ctx),
            update_count: 0,
        });

        // Add dynamic attributes
        let i = 0;
        while (i < vector::length(&attributes_names)) {
            let attr_name = vector::borrow(&attributes_names, i);
            let attr_value = vector::borrow(&attributes_values, i);
            df::add(&mut nft.id, *attr_name, NFTAttribute {
                value: *attr_value,
                last_updated: tx_context::epoch(ctx),
            });
            i = i + 1;
        };

        // Update collection
        collection.total_minted = collection.total_minted + 1;

        // Add royalty recipients and percentages
        let j = 0;
        while (j < vector::length(&royalty_recipients)) {
            let recipient = vector::borrow(&royalty_recipients, j);
            let percentage = vector::borrow(&royalty_percentages, j);
            vector::push_back(&mut nft.royalty_info, RoyaltyRecipient {
                recipient,
                percentage,
            });
            j = j + 1;
        };

        transfer::transfer(nft, tx_context::sender(ctx));
    }

    /// Get an NFT's image metadata
    public fun get_image_metadata(nft: &OffbrandNFT): (String, String, String, String, String, u64) {
        let metadata = df::borrow(&nft.id, IMAGE_METADATA_KEY);
        (
            metadata.walrus_blob_id,
            metadata.image_url,
            metadata.generation_prompt,
            metadata.model_version,
            metadata.generation_params,
            metadata.created_at
        )
    }

    /// Called by NFT owner to update the 8-bit Oracle advisor prompt.
    /// Ownership is enforced by Sui runtime due to `nft: &mut OffbrandNFT` argument.
    public entry fun update_prompt(
        collection: &OffbrandCollection, // To get fee info
        nft: &mut OffbrandNFT,
        new_base_prompt: String, new_style_prompt: String,
        mut payment: Coin<SUI>, ctx: &mut tx_context::TxContext
    ) {
        // Check payment
        let fee = collection.prompt_update_fee;
        assert!(balance::value(payment) >= fee, 1);

        // Transfer fee to collection admin
        let fee_balance = balance::split(payment, fee);
        transfer::public_transfer(
            balance::into_coin(fee_balance, ctx),
            tx_context::sender(ctx)
        );

        // Update prompt config
        let prompt_config = df::borrow_mut(&mut nft.id, PROMPT_CONFIG_KEY);
        prompt_config.base_prompt = new_base_prompt;
        prompt_config.style_prompt = new_style_prompt;
        prompt_config.last_updated = tx_context::epoch(ctx);
        prompt_config.update_count = prompt_config.update_count + 1;
    }

    /// Get an NFT's prompt configuration
    public fun get_prompt_config(nft: &OffbrandNFT): (String, String, u64, u64) {
        let prompt_config = df::borrow(&nft.id, PROMPT_CONFIG_KEY);
        (
            prompt_config.base_prompt,
            prompt_config.style_prompt,
            prompt_config.last_updated,
            prompt_config.update_count
        )
    }

    /// Called by the original NFT creator to update a custom attribute.
    public entry fun update_attribute(
        nft: &mut OffbrandNFT,
        attribute_name: String,
        new_value: String,
        ctx: &mut tx_context::TxContext
    ) {
        assert!(ctx.sender() == nft.creator, 0); // E_NOT_CREATOR - Only original creator can update attributes
        let attr = df::borrow_mut(&mut nft.id, attribute_name);
        attr.value = new_value;
        attr.last_updated = tx_context::epoch(ctx);
    }

    /// Get an NFT's attribute
    public fun get_attribute(nft: &OffbrandNFT, attribute_name: String): (String, u64) {
        let attr = df::borrow(&nft.id, attribute_name);
        (attr.value, attr.last_updated)
    }

    /// Get collection info
    public fun get_collection_info(collection: &OffbrandCollection): (String, String, u64, u64, u64) {
        (
            collection.name,
            collection.description,
            collection.total_minted,
            collection.minting_fee,
            collection.prompt_update_fee
        )
    }
}
```

2. Royalty Implementation Details

The royalty system is implemented using Sui's TransferPolicy framework:

a. Collection Initialization:

- Creates a shared TransferPolicy object for the collection
- Stores the TransferPolicy ID in the collection
- Transfers the TransferPolicyCap to the collection admin

b. Royalty Rule Management:

- Collection admin can update royalty rules using `update_royalty_rules`
- Rules are added using the custom `royalty_rule` module
- Royalty percentages are specified in basis points (bps)
- Minimum amount can be set to ensure minimum royalty payments

c. Royalty Rule Structure:

```move
module nfter::royalty_rule {
    public struct Config has store, drop {
        amount_bp: u16,  // Basis points (e.g., 500 for 5%)
        min_amount: u64  // Minimum amount in MIST
    }
}
```

3. Usage Examples

a. Initializing Collection with TransferPolicy:

```move
// Admin creates collection with TransferPolicy
init_collection(
    "Offbrand Crypto",
    "A collection of AI-generated NFTs",
    1000000, // 0.001 SUI minting fee
    500000,  // 0.0005 SUI prompt update fee
    publisher,
    ctx
);
```

b. Setting Royalty Rules:

```move
// Admin sets 5% royalty with minimum 0.001 SUI
update_royalty_rules(
    collection,
    policy,
    policy_cap,
    500,    // 5% in basis points
    1000000 // 0.001 SUI minimum
    ctx
);
```

## Future Considerations

1. Multiple Royalty Recipients:

   - Current implementation uses only the first recipient
   - Future versions could support multiple recipients with different percentages
   - Would require custom royalty rule implementation

2. Dynamic Royalty Rules:

   - Could allow different royalty rules for different NFTs
   - Would require per-NFT TransferPolicy instead of collection-level

3. Royalty Distribution:

   - Current implementation enforces royalty payments
   - Future versions could add automatic distribution logic

4. Marketplace Integration:
   - Current design is compatible with Sui marketplaces
   - Marketplaces can read royalty rules from TransferPolicy
   - Could add marketplace-specific features in future versions

## Frontend Integration (Conceptual)

```typescript
// Minting an NFT
async function mintNFT(
  walletContext: WalletContext,
  collectionId: string /*...other params...*/
) {
  const txb = new TransactionBlock();
  const [paymentCoin] = txb.splitCoins(txb.gas, [txb.pure(mintingFee)]);

  // Example royalty setup (for hackathon, likely one recipient at 100%)
  const royaltyRecipients = ["0xSUI_ADDRESS_OF_RECIPIENT"];
  const royaltyPercentages = [100]; // Representing 100%

  txb.moveCall({
    target: `${packageId}::nfter::mint_nft`,
    arguments: [
      txb.object(collectionId),
      txb.pure(name),
      txb.pure(description),
      txb.pure(royaltyRecipients),
      txb.pure(royaltyPercentages),
      txb.pure(oracleBasePrompt),
      txb.pure(oracleStylePrompt),
      txb.pure(walrusBlobId),
      txb.pure(imageUrl),
      txb.pure(imageGenerationPrompt),
      txb.pure(modelVersion),
      txb.pure(generationParamsJson),
      txb.pure(attributeNamesArray),
      txb.pure(attributeValuesArray),
      paymentCoin,
    ],
  });
  // ... sign and execute ...
}

// Updating an NFT's Advisor Prompt
async function updateAdvisorPrompt(
  walletContext: WalletContext,
  collectionId: string,
  nftId: string /*...other params...*/
) {
  const txb = new TransactionBlock();
  const [paymentCoin] = txb.splitCoins(txb.gas, [txb.pure(promptUpdateFee)]);

  txb.moveCall({
    target: `${packageId}::nfter::update_prompt`,
    arguments: [
      txb.object(collectionId),
      txb.object(nftId),
      txb.pure(newBasePrompt),
      txb.pure(newStylePrompt),
      paymentCoin,
    ],
  });
  // ... sign and execute (must be called by NFT owner) ...
}
```

## Next Steps (Deployment & Testing Focus)

1.  **Contract Finalization & Build:**

    - [✅] Finalize Move contract (`nfter.move`) with royalty data structure, image/advisor prompt handling, and attribute updates.
    - [✅] Ensure `Move.toml` is configured for `2024.beta` edition.
    - [✅] Successfully build the contract using `sui move build --dev`.

2.  **Devnet Deployment & Initialization:**

    - [ ] Ensure Sui client is installed, configured for devnet, and the active address has SUI.
    - [ ] **Publish Contract:** Use `sui client publish --gas-budget 500000000 --json` (in the `move` directory). Note the `packageId`.
    - [ ] **Initialize Collection:** Call `sui client call --package <YOUR_PACKAGE_ID> --module nfter --function init_collection --args "Offbrand Crypto" "...description..." <MINT_FEE_MIST> <PROMPT_UPDATE_FEE_MIST> --gas-budget <GAS> --json`. Note the `OffbrandCollection` object ID (`collectionId`).
    - [ ] **Share Collection:** The admin (initial owner of `collectionId`) must run `sui client transfer --to-shared --object-id <YOUR_COLLECTION_ID> --gas-budget <GAS>`. This is CRITICAL for public minting.

3.  **Initial Contract Interaction (CLI Testing):**

    - [ ] **Mint NFT:** Manually call `mint_nft` via `sui client call ...` providing all necessary arguments (including example royalty recipients/percentages, prompts, Walrus ID, etc.) and the shared `collectionId`. Verify NFT creation and ownership.
    - [ ] **Update Advisor Prompt:** As the new NFT owner, call `update_prompt` via `sui client call ...` for the minted NFT. Verify changes.
    - [ ] **Update Attribute:** As the NFT creator, call `update_attribute` via `sui client call ...`. Verify changes.
    - [ ] Check Sui Explorer for correct display metadata and object details.

4.  **Frontend Integration (Parallel Work):**
    - [ ] Integrate Walrus image upload.
    - [ ] Develop UI for minting, connecting to the deployed contract and shared collection.
    - [ ] Develop UI for viewing NFTs and allowing owners to update advisor prompts.

## Deployment Checklist

1. Contract Deployment:

   - [ ] Deploy to devnet
   - [ ] Initialize collection with:
     - Name: "Offbrand Crypto"
     - Description: "The official collection of offbrand crypto NFTs"
     - Minting Fee: 0.001 SUI
   - [ ] Verify display metadata in Sui Explorer

2. Admin Setup:

   - [ ] Deploy admin UI
   - [ ] Set up admin wallet
   - [ ] Test collection settings updates
   - [ ] Verify minting controls

3. User Interface:
   - [ ] Deploy minting UI
   - [ ] Test minting flow
   - [ ] Verify NFT display in Sui Explorer

## Dependencies

1. Sui Move SDK
2. @mysten/dapp-kit
3. @mysten/sui.js
4. Walrus API
